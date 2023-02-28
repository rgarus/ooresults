# Copyright (C) 2022 Rainer Garus
#
# This file is part of the ooresults Python package, a software to
# compute results of orienteering events.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio
import copy
import json
import pathlib
import datetime
import bz2
import functools
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import tzlocal
import websockets
from websockets.legacy.server import WebSocketServerProtocol
import web

from ooresults.utils.globals import t_globals
from ooresults.handler import model
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo import result_type
from ooresults.repo.result_type import ResultStatus

templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


class WebSocketHandler:
    def __init__(self, demo_reader: bool = False):
        self.demo_reader = demo_reader
        self.connections = {}
        self.messages = []
        self.cardreader_status = {}
        self.executor = ThreadPoolExecutor(max_workers=2)

        #
        # Cardreader status:
        #
        # offline
        # online
        # readerDisconnected
        # readerConnected
        # cardInserted
        # cardRemoved
        # cardRead
        #

    async def update_event(self, event: Dict) -> None:
        if event:
            connections = {
                k: v
                for k, v in self.connections.items()
                if v[0] == "/si2" and str(event["id"]) == v[1]
            }
            if connections:
                await asyncio.wait(
                    [
                        self.send(conn=conn, event=copy.deepcopy(event), message={})
                        for conn in connections
                    ]
                )

    async def send_to_all(self, event: Dict, message: Dict = {}) -> None:
        if event:
            connections = {
                k: v for k, v in self.connections.items() if str(event["id"]) == v[1]
            }
            if connections:
                await asyncio.wait(
                    [
                        self.send(
                            conn=conn, event=copy.deepcopy(event), message=message
                        )
                        for conn in connections
                    ]
                )

    async def send(
        self, conn: WebSocketServerProtocol, event: Dict, message: Dict = {}
    ) -> None:
        status = (
            self.cardreader_status[event["id"]]
            if event and event["id"] in self.cardreader_status
            else "offline"
        )
        path, event_id, event_key = self.connections[conn]
        if path == "/si2":
            data = render.si.si2_data(status, event, self.messages)
        else:
            if status != "cardRead":
                data = message.get("controlCard", "")
            elif message.get("error", None) is not None:
                data = render.si.si1_error(message)
            elif message.get("lastName", None) is not None:
                data = render.si.si1_data(message)
            else:
                return
            data = json.dumps({"status": status, "data": str(data)})
        print("WEBSOCKET SEND ...", conn)
        await conn.send(str(data))

    async def handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        print("WEBSOCKET CONNECTED")
        print("websocket:", websocket)
        print("websocket.request_headers:", websocket.request_headers)
        print("path:", path)

        if path == "/demo":
            event = None
            try:
                if self.demo_reader:
                    async for message in websocket:
                        # workaround to detect lost websocket connection in the browser
                        # see https://stackoverflow.com/questions/26971026/handling-connection-loss-with-websockets
                        if message == "__ping__":
                            await websocket.send("__pong__")
                        else:
                            print("WEBSOCKET RECEIVED", websocket, message)

                            item = json.loads(message)
                            #
                            # item = {
                            #     'key': 4711,
                            #     'code': ['Check', 'Start', '', '', '', '', '', '', '', '', 'Finish'],
                            #     'time': ['10:11:12', '', '', '', '', '', '', '', '', '', '10:23:23'],
                            #     'card': '1111',
                            # }
                            #

                            d = {
                                "entryType": "cardRead",
                                "entryTime": datetime.datetime.now(),
                                "controlCard": item.get("card", None),
                                "result": None,
                            }

                            # add the event date to the times entered on the webpage
                            events = await asyncio.get_event_loop().run_in_executor(
                                executor=self.executor, func=model.get_events
                            )
                            date_of_event = datetime.date.today()
                            for e in events:
                                if e.key == item.get("key", None):
                                    date_of_event = e.date
                                    break

                            def parse_time(value: str) -> datetime.datetime:
                                return datetime.datetime.combine(
                                    date=date_of_event,
                                    time=datetime.datetime.strptime(
                                        value, "%H:%M:%S"
                                    ).time(),
                                    tzinfo=tzlocal.get_localzone(),
                                )

                            result = result_type.PersonRaceResult(
                                status=ResultStatus.FINISHED
                            )
                            _code = item["code"]
                            _time = item["time"]
                            if _code[0] == "Check" and _time[0] != "":
                                result.punched_check_time = parse_time(_time[0])
                            if _code[1] == "Start" and _time[1] != "":
                                result.punched_start_time = parse_time(_time[1])
                            if _code[-1] == "Finish" and _time[-1] != "":
                                result.punched_finish_time = parse_time(_time[-1])

                            result.start_time = result.punched_start_time
                            result.finish_time = result.punched_finish_time
                            for i in range(2, 10):
                                if _code[i] != "" and _time[i] != "":
                                    result.split_times.append(
                                        result_type.SplitTime(
                                            control_code=_code[i],
                                            punch_time=parse_time(_time[i]),
                                            status="Additional",
                                        )
                                    )
                            d["result"] = result

                            try:
                                (
                                    status,
                                    event,
                                    res,
                                ) = await asyncio.get_event_loop().run_in_executor(
                                    executor=self.executor,
                                    func=functools.partial(
                                        model.store_cardreader_result,
                                        event_key=item["key"],
                                        item=d,
                                    ),
                                )
                            except EventNotFoundError as e:
                                raise RuntimeError(str(e))
                            except Exception as e:
                                traceback.print_exc()
                                raise RuntimeError(str(e))

                            self.cardreader_status[event["id"]] = status

                            if "entryTime" in res:
                                res["entryTime"] = res["entryTime"].strftime("%H:%M:%S")

                            if status == "cardRead":
                                self.messages.append(res.copy())
                            await self.send_to_all(
                                event=event.copy(), message=res.copy()
                            )

                            res["readerStatus"] = status
                            res["event"] = event["name"]
                            if "status" in res:
                                res["status"] = res["status"].name
                            print(res)

            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                print("WEBSOCKET CONNECTION CLOSED", websocket)
                if event:
                    if event["id"] in self.cardreader_status:
                        del self.cardreader_status[event["id"]]
                    await self.send_to_all(event=event.copy(), message={})

        elif path == "/cardreader":
            event = None
            event_key = websocket.request_headers.get("X-Event-Key", "")
            try:
                print(">>>>>>>>>>> cardreader", event_key)
                async for message in websocket:
                    try:
                        data = bz2.decompress(message)
                    except:
                        raise RuntimeError("Data not bz2 encoded")

                    try:
                        item = json.loads(data.decode())
                    except:
                        raise RuntimeError("Data not json deserialisable")

                    try:
                        item = model.parse_cardreader_log(item=item)
                    except Exception as e:
                        raise RuntimeError(str(e))

                    try:
                        (
                            status,
                            event,
                            res,
                        ) = await asyncio.get_event_loop().run_in_executor(
                            executor=self.executor,
                            func=functools.partial(
                                model.store_cardreader_result,
                                event_key=event_key,
                                item=item,
                            ),
                        )
                    except EventNotFoundError as e:
                        raise RuntimeError(str(e))
                    except Exception as e:
                        traceback.print_exc()
                        raise RuntimeError(str(e))

                    self.cardreader_status[event["id"]] = status

                    if "entryTime" in res:
                        res["entryTime"] = res["entryTime"].strftime("%H:%M:%S")

                    if status == "cardRead":
                        self.messages.append(res.copy())
                    await self.send_to_all(event=event.copy(), message=res.copy())

                    res["readerStatus"] = status
                    res["event"] = event["name"]
                    if "status" in res:
                        res["status"] = res["status"].name
                    print(res)
                    await websocket.send(json.dumps(res))

            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                await websocket.send(str(e))
                print(str(e))
            finally:
                print("CARDREADER CONNECTION CLOSED", websocket)
                if event:
                    if event["id"] in self.cardreader_status:
                        del self.cardreader_status[event["id"]]
                    await self.send_to_all(event=event.copy(), message={})

        else:
            try:
                if path in ("/si1", "/si2"):
                    data = await websocket.recv()
                    event_id, event_key = data.split(",")

                    # check event key
                    events = await asyncio.get_event_loop().run_in_executor(
                        executor=self.executor, func=model.get_events
                    )
                    for e in events:
                        if str(e.id) == event_id and e.key == event_key:
                            self.connections[websocket] = (path, event_id, event_key)
                            await self.send(conn=websocket, event=e, message={})
                            async for message in websocket:
                                # workaround to detect lost websocket connection in the browser
                                # see https://stackoverflow.com/questions/26971026/handling-connection-loss-with-websockets
                                if message == "__ping__":
                                    await websocket.send("__pong__")
                                else:
                                    print("WEBSOCKET RECEIVED", websocket, message)
                                    break
                    else:
                        await websocket.send("__no_access__")
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                if websocket in self.connections:
                    del self.connections[websocket]
                print("WEBSOCKET CONNECTION CLOSED", websocket)

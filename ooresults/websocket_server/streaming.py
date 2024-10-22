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
import bz2
import copy
import functools
import json
import logging
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import websockets

from ooresults.model import model
from ooresults.plugins import iof_result_list
from ooresults.repo.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.websocket_server import streaming_status


class Streaming:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.tasks: Dict[int, asyncio.Task] = {}
        self.events: Dict[int, EventType] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)

        events = model.get_events()
        for event in events:
            if event.streaming_enabled:
                e = copy.deepcopy(event)
                self.events[event.id] = e
                self.tasks[event.id] = self.loop.create_task(coro=self.stream(event=e))

    async def update_event(self, event: EventType):
        if event.id in self.tasks:
            e = self.events[event.id]
            if (
                event.streaming_enabled != e.streaming_enabled
                or event.streaming_address != e.streaming_address
                or event.streaming_key != e.streaming_key
            ):
                task = self.tasks[event.id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if event.id not in self.tasks and event.streaming_enabled:
            e = copy.deepcopy(event)
            self.events[event.id] = e
            self.tasks[event.id] = asyncio.create_task(coro=self.stream(event=e))

    async def stream(self, event: EventType) -> None:
        try:
            await streaming_status.status.set(
                event=event,
                status=streaming_status.Status.SERVER_NOT_REACHABLE,
            )

            uri = f"wss://{event.streaming_address}/import"
            headers = {
                "Content-Type": "application/octet-stream",
                "X-Event-Key": event.streaming_key,
                "X-Suffix": ".json",
            }

            ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            while True:
                websocket = None
                while websocket is None:
                    try:
                        websocket = await websockets.connect(
                            uri=uri,
                            ssl=ssl_context,
                            extra_headers=headers,
                        )
                        break
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        await streaming_status.status.set(
                            event=event,
                            status=streaming_status.Status.SERVER_NOT_REACHABLE,
                        )
                        websocket = None
                        await asyncio.sleep(delay=10)

                sent_event = None
                sent_class_results = None
                result = None

                while True:
                    wait_time = 15
                    try:
                        (
                            act_event,
                            act_class_results,
                        ) = await asyncio.get_event_loop().run_in_executor(
                            executor=self.executor,
                            func=functools.partial(
                                model.event_class_results,
                                event_id=event.id,
                            ),
                        )

                        if (
                            sent_event != act_event
                            or sent_class_results != act_class_results
                        ):
                            sent_event = act_event
                            sent_class_results = act_class_results

                            content = iof_result_list.create_result_list(
                                event=act_event,
                                class_results=act_class_results,
                                status=iof_result_list.ResultListStatus.SNAPSHOT,
                            )
                            data = bz2.compress(content)

                            try:
                                await websocket.send(data)
                                answer = await asyncio.wait_for(websocket.recv(), 10)

                                answer = json.loads(answer)
                                result = answer.get("result", "error")
                            except (asyncio.TimeoutError, json.decoder.JSONDecodeError):
                                result = "error"

                            if result == "ok":
                                await streaming_status.status.set(
                                    event=act_event,
                                    status=streaming_status.Status.OK,
                                )
                            elif result == "eventNotFound":
                                await streaming_status.status.set(
                                    event=act_event,
                                    status=streaming_status.Status.EVENT_NOT_FOUND,
                                )
                                await asyncio.sleep(delay=30)
                                break
                            else:
                                sent_event = None
                                sent_class_results = None
                                await streaming_status.status.set(
                                    event=act_event,
                                    status=streaming_status.Status.ERROR,
                                )

                        try:
                            await asyncio.wait_for(websocket.recv(), 30)
                        except asyncio.TimeoutError:
                            wait_time = 0
                        else:
                            # if no exception is raised, an unexpected answer is received
                            # set the status to error and close the connection
                            await websocket.close()
                            await streaming_status.status.set(
                                event=act_event,
                                status=streaming_status.Status.ERROR,
                            )

                    except (EventNotFoundError, asyncio.CancelledError):
                        raise
                    except Exception:
                        logging.exception(msg="", exc_info=True, stack_info=True)
                    finally:
                        if not result:
                            await streaming_status.status.set(
                                event=event,
                                status=streaming_status.Status.ACCESS_DENIED,
                            )
                        await asyncio.sleep(delay=wait_time)
                        if websocket.closed:
                            break

        except asyncio.CancelledError:
            raise
        except EventNotFoundError:
            pass
        except Exception:
            logging.exception(msg="", exc_info=True, stack_info=True)
        finally:
            del self.events[event.id]
            del self.tasks[event.id]
            await streaming_status.status.delete(event=event)

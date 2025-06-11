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
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import websockets.exceptions
from websockets.asyncio.client import connect
from websockets.protocol import State

from ooresults import model
from ooresults.otypes.event_type import EventType
from ooresults.plugins import iof_result_list
from ooresults.repo.repo import EventNotFoundError
from ooresults.websocket_server import streaming_status


class Streaming:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.tasks: Dict[int, asyncio.Task] = {}
        self.events: Dict[int, EventType] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)

        events = model.events.get_events()
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
                del self.events[event.id]
                del self.tasks[event.id]

        if event.id not in self.tasks and event.streaming_enabled:
            e = copy.deepcopy(event)
            self.events[event.id] = e
            self.tasks[event.id] = asyncio.create_task(coro=self.stream(event=e))

    async def stream(self, event: EventType) -> None:
        try:
            await streaming_status.status.set(
                event=event,
                status=streaming_status.Status.NOT_CONNECTED,
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
                        websocket = await connect(
                            uri=uri,
                            ssl=ssl_context,
                            additional_headers=headers,
                        )
                        break
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        await streaming_status.status.set(
                            event=event,
                            status=streaming_status.Status.NOT_CONNECTED,
                            comment=str(e),
                        )
                        websocket = None
                        await asyncio.sleep(delay=20)

                # websocket is opened
                sent_event = None
                sent_class_results = None
                result = None

                while True:
                    error = False
                    wait_time = 0
                    try:
                        # compute actual result
                        (
                            act_event,
                            act_class_results,
                        ) = await asyncio.get_event_loop().run_in_executor(
                            executor=self.executor,
                            func=functools.partial(
                                model.results.event_class_results,
                                event_id=event.id,
                            ),
                        )

                        # send actual result as IOF result list only if it has changed
                        if (
                            sent_event != act_event
                            or sent_class_results != act_class_results
                        ):
                            content = iof_result_list.create_result_list(
                                event=act_event,
                                class_results=act_class_results,
                                status=iof_result_list.ResultListStatus.SNAPSHOT,
                            )
                            data = bz2.compress(content)

                            await websocket.send(data)
                            answer = await asyncio.wait_for(websocket.recv(), 30)

                            answer = json.loads(answer)
                            result = answer["result"]

                            if result == "ok":
                                sent_event = act_event
                                sent_class_results = act_class_results

                                # new state: OK
                                await streaming_status.status.set(
                                    event=act_event,
                                    status=streaming_status.Status.OK,
                                )
                            elif result == "eventNotFound":
                                # new state: EVENT_NOT_FOUND (on live server)
                                await streaming_status.status.set(
                                    event=act_event,
                                    status=streaming_status.Status.EVENT_NOT_FOUND,
                                )
                                wait_time = 45
                                break
                            else:
                                # new state: ERROR
                                error = True

                        try:
                            await asyncio.wait_for(websocket.recv(), 30)
                        except asyncio.TimeoutError:
                            # no data received, this is ok
                            pass
                        else:
                            # if no exception is raised, an unexpected answer is received
                            # set the status to error and close the connection
                            await websocket.close()
                            # new state: ERROR
                            error = True
                            wait_time = 15

                    except asyncio.TimeoutError:
                        # new state: ERROR
                        error = True
                        wait_time = 15
                        break
                    except (json.decoder.JSONDecodeError, KeyError):
                        # new state: ERROR
                        error = True
                        wait_time = 45
                        break
                    except (EventNotFoundError, asyncio.CancelledError):
                        raise
                    except websockets.exceptions.ConnectionClosed:
                        await streaming_status.status.set(
                            event=event,
                            status=streaming_status.Status.NOT_CONNECTED,
                        )
                        wait_time = 30
                        break
                    except Exception:
                        logging.exception(msg="", exc_info=True, stack_info=True)
                        # new state: ERROR
                        await streaming_status.status.set(
                            event=event,
                            status=streaming_status.Status.INTERNAL_ERROR,
                        )
                        wait_time = 30
                        break
                    finally:
                        if error:
                            # If after connecting and sending the result no or no correct
                            # answer is received, we can not decide if we are connected
                            # to an ooresults server not working correctly or to something
                            # else. In this case we set the status to protocol error.
                            if result:
                                await streaming_status.status.set(
                                    event=event,
                                    status=streaming_status.Status.ERROR,
                                )
                            else:
                                await streaming_status.status.set(
                                    event=event,
                                    status=streaming_status.Status.PROTOCOL_ERROR,
                                )
                        await asyncio.sleep(delay=wait_time)
                        if websocket.state == State.CLOSED:
                            break

        except asyncio.CancelledError:
            raise
        except EventNotFoundError:
            pass
        except Exception:
            logging.exception(msg="", exc_info=True, stack_info=True)
        finally:
            if (
                event.id in self.tasks
                and self.tasks[event.id] == asyncio.current_task()
            ):
                del self.events[event.id]
                del self.tasks[event.id]
            await streaming_status.status.delete(event=event)

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


import logging
import threading
from collections.abc import Awaitable
from collections.abc import Callable
from enum import Enum
from typing import Optional

from ooresults.otypes.event_type import EventType


class Status(Enum):
    NOT_CONNECTED = "NotConnected"
    INTERNAL_ERROR = "InternalError"
    PROTOCOL_ERROR = "ProtocolError"
    EVENT_NOT_FOUND = "EventNotFound"
    ERROR = "Error"
    OK = "Ok"


class StreamingStatus:
    def __init__(self) -> None:
        self.status: dict[int, Status] = {}
        self.lock = threading.Lock()
        self.callback: Optional[Callable[[EventType], Awaitable[None]]] = None

    def get(self, id: int) -> Optional[Status]:
        with self.lock:
            return self.status.get(id, None)

    async def set(self, event: EventType, status: Status, comment: str = "") -> None:
        with self.lock:
            changed = self.status.get(event.id, None) != status
            self.status[event.id] = status
        if changed:
            logging.info(f"Streaming status: {status}, {comment}")
        if changed and self.callback:
            await self.callback(event)

    async def delete(self, event: EventType) -> None:
        with self.lock:
            if event.id in self.status:
                del self.status[event.id]
        if self.callback:
            await self.callback(event)

    def register(
        self, callback: Optional[Callable[[EventType], Awaitable[None]]]
    ) -> None:
        self.callback = callback


status = StreamingStatus()

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


import threading
from enum import Enum
from typing import Dict
from typing import Optional
from typing import Awaitable

from ooresults.repo.event_type import EventType


class Status(Enum):
    SERVER_NOT_REACHABLE = "ServerNotReachable"
    ACCESS_DENIED = "AccessDenied"
    EVENT_NOT_FOUND = "EventNotFound"
    ERROR = "Error"
    OK = "Ok"


class StreamingStatus:
    def __init__(self):
        self.status: Dict[int, Status] = {}
        self.lock = threading.Lock()
        self.awaitable = None

    def get(self, id: int) -> Optional[Status]:
        with self.lock:
            return self.status.get(id, None)

    async def set(self, event: EventType, status: Status) -> None:
        with self.lock:
            changed = self.status.get(event.id, None) != status
            self.status[event.id] = status
        if changed and self.awaitable:
            await self.awaitable(event)

    async def delete(self, event: EventType) -> None:
        with self.lock:
            if event.id in self.status:
                del self.status[event.id]
        if self.awaitable:
            await self.awaitable(event)

    def register(self, awaitable: Optional[Awaitable[EventType]]) -> None:
        self.awaitable = awaitable


status = StreamingStatus()

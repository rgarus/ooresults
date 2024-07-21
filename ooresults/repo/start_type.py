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


import dataclasses
import json
from datetime import datetime
from typing import Optional


def to_isoformat(value: Optional[datetime]) -> Optional[str]:
    if value is not None:
        return value.isoformat()
    else:
        return None


def from_isoformat(value: Optional[str]) -> Optional[datetime]:
    if value:
        return datetime.fromisoformat(value)
    else:
        return None


@dataclasses.dataclass
class PersonRaceStart:
    start_time: Optional[datetime] = None

    @classmethod
    def from_dict(cls, o: dict):
        return PersonRaceStart(
            start_time=from_isoformat(value=o.get("startTime")),
        )

    @classmethod
    def from_json(cls, json_data: str):
        return PersonRaceStart.from_dict(o=json.loads(json_data))

    def to_dict(self) -> dict:
        d = {}
        if self.start_time is not None:
            d["startTime"] = to_isoformat(self.start_time)
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

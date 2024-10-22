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
from datetime import datetime
from typing import List
from typing import Optional


@dataclasses.dataclass
class EventType:
    id: int
    name: str
    date: datetime.date
    key: Optional[str]
    publish: bool
    series: Optional[str]
    fields: List[str]
    streaming_address: Optional[str] = None
    streaming_key: Optional[str] = None
    streaming_enabled: Optional[bool] = None

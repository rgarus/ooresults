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
from dataclasses import field
from typing import Dict
from typing import Optional

from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.start_type import PersonRaceStart


@dataclasses.dataclass
class EntryType:
    id: int
    event_id: int
    competitor_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str] = None
    year: Optional[int] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    not_competing: bool = False
    chip: Optional[str] = None
    fields: Dict[int, str] = field(default_factory=lambda: {})
    result: PersonRaceResult = field(default_factory=lambda: PersonRaceResult())
    start: PersonRaceStart = field(default_factory=lambda: PersonRaceStart())
    club_id: Optional[int] = None
    club_name: Optional[str] = None


@dataclasses.dataclass
class RankedEntryType:
    entry: EntryType
    rank: Optional[int] = None
    time_behind: Optional[int] = None

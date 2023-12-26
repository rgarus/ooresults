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
from decimal import Decimal
from typing import Optional
from typing import Dict


@dataclasses.dataclass
class Settings:
    name: str = ""
    nr_of_best_results: Optional[int] = None
    mode: str = "Proportional"
    maximum_points: int = 100
    decimal_places: int = 2


@dataclasses.dataclass
class Points:
    points: Decimal
    bonus: bool = False


@dataclasses.dataclass
class PersonSeriesResult:
    last_name: str
    first_name: str
    year: Optional[int]
    club_name: Optional[str]
    races: Dict[int, Points]
    total_points: Decimal
    rank: Optional[int]

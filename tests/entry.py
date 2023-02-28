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


from typing import Optional

from ooresults.repo import result_type


class Entry:
    def __init__(
        self,
        id: int = 0,
        event_id: int = 0,
        first_name: str = "",
        last_name: str = "",
        gender: str = "",
        year: Optional[int] = None,
        not_competing: bool = False,
        competitor_id: int = 0,
        class_id: int = 0,
        class_: str = "",
        club: str = "",
        club_id: Optional[int] = None,
        chip: str = "",
        result: result_type.PersonRaceResult = result_type.PersonRaceResult(),
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.year = year
        self.not_competing = not_competing
        self.competitor_id = competitor_id
        self.class_id = class_id
        self.class_ = class_
        self.club = club
        self.club_id = club_id
        self.chip = chip
        self.result = result

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def get(self, key, default):
        return getattr(self, key, default)

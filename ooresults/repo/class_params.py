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

import caseconverter
import fastclasses_json


@fastclasses_json.dataclass_json(field_name_transform=caseconverter.camelcase)
@dataclasses.dataclass
class VoidedLeg:
    control_1: str
    control_2: str


@fastclasses_json.dataclass_json(field_name_transform=caseconverter.camelcase)
@dataclasses.dataclass
class ClassParams:
    otype: str = "standard"
    using_start_control: str = "if_punched"
    mass_start: Optional[datetime] = None
    time_limit: Optional[int] = None
    penalty_controls: Optional[int] = None
    penalty_overtime: Optional[int] = None
    apply_handicap_rule: bool = False
    voided_legs: List[VoidedLeg] = dataclasses.field(default_factory=list)

    #
    # possible values for using_start_control
    #   if_punched: if the start control station is punched, the punching time is used,
    #               if the start control station is not punched, the start time of the competitor is used
    #   yes: if the start control station is not punched, the race status is 'MissingPunch'
    #   no:  a punched start control station is ignored
    #
    # possible values for otype:
    #   standard: classic orienteering (control stations must be punched in given order)
    #   net:      control stations can be punched in arbitrary order
    #   score:
    #

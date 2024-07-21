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


import json
import dataclasses
from datetime import datetime
from typing import List
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
class VoidedLeg:
    control_1: str
    control_2: str

    @classmethod
    def from_dict(cls, o: dict):
        return VoidedLeg(
            control_1=o["control1"],
            control_2=o["control2"],
        )

    @classmethod
    def from_json(cls, json_data: str):
        return VoidedLeg.from_dict(o=json.loads(json_data))

    def to_dict(self) -> dict:
        return {
            "control1": self.control_1,
            "control2": self.control_2,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


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

    @classmethod
    def from_dict(cls, o: dict):
        voided_legs = []
        for voided_leg in o["voidedLegs"]:
            voided_legs.append(VoidedLeg.from_dict(o=voided_leg))

        return ClassParams(
            otype=o["otype"],
            using_start_control=o["usingStartControl"],
            mass_start=from_isoformat(value=o.get("massStart")),
            time_limit=o.get("timeLimit"),
            penalty_controls=o.get("penaltyControls"),
            penalty_overtime=o.get("penaltyOvertime"),
            apply_handicap_rule=o["applyHandicapRule"],
            voided_legs=voided_legs,
        )

    @classmethod
    def from_json(cls, json_data: str):
        return ClassParams.from_dict(o=json.loads(json_data))

    def to_dict(self) -> dict:
        voided_legs = self.voided_legs
        if voided_legs is not None:
            voided_legs = [voided_leg.to_dict() for voided_leg in voided_legs]

        d = {}
        d["otype"] = self.otype
        d["usingStartControl"] = self.using_start_control
        if self.mass_start is not None:
            d["massStart"] = to_isoformat(self.mass_start)
        if self.time_limit is not None:
            d["timeLimit"] = self.time_limit
        if self.penalty_controls is not None:
            d["penaltyControls"] = self.penalty_controls
        if self.penalty_overtime is not None:
            d["penaltyOvertime"] = self.penalty_overtime
        d["applyHandicapRule"] = self.apply_handicap_rule
        d["voidedLegs"] = voided_legs
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

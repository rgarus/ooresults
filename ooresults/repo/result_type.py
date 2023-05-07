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


from __future__ import annotations

import dataclasses
from datetime import datetime
import enum
from typing import List
from typing import Optional
from typing import Dict

from ooresults.handler import handicap
from ooresults.repo.class_params import ClassParams


@dataclasses.dataclass
class SplitTime:
    control_code: str
    punch_time: Optional[datetime] = None
    time: Optional[int] = None
    status: Optional[str] = None
    leg_voided: bool = False

    def recalculate_time(self, start_time: Optional[datetime]) -> None:
        """
        set time as difference between start_time and punch_time
        """
        if start_time is not None and self.punch_time is not None:
            diff = self.punch_time.replace(microsecond=0) - start_time.replace(
                microsecond=0
            )
            self.time = int(diff.total_seconds())

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def get(self, key, default):
        return getattr(self, key, default)


class ResultStatus(enum.Enum):
    INACTIVE = 0
    FINISHED = 2
    OK = 3
    MISSING_PUNCH = 4
    DID_NOT_START = 5
    DID_NOT_FINISH = 6
    OVER_TIME = 7
    DISQUALIFIED = 8


@dataclasses.dataclass
class PersonRaceResult:
    status: ResultStatus = ResultStatus.INACTIVE
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    punched_clear_time: Optional[datetime] = None
    punched_check_time: Optional[datetime] = None
    punched_start_time: Optional[datetime] = None
    punched_finish_time: Optional[datetime] = None
    time: Optional[int] = None
    split_times: List[SplitTime] = dataclasses.field(default_factory=list)
    last_leg_voided: bool = False
    extensions: Dict = dataclasses.field(default_factory=dict)

    #
    # keys of extensions are:
    #   factor: float            -- handicap factor
    #   penalties_controls: int  -- penalty for missing controls in seconds
    #   penalties_overtime: int  -- penalty for exceeding the time limit in seconds
    #   running_time: int        -- running time (= finish time - start time)
    #   score_controls: float    -- score points for controls
    #   score_overtime: float    -- score points to subtract for exceeding the time limit
    #   score: float             -- total score points (score_controls - score_overtime)
    #

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def get(self, key, default):
        return getattr(self, key, default)

    def has_punches(self) -> bool:
        return (
            self.punched_start_time is not None
            or self.punched_finish_time is not None
            or [p for p in self.split_times if p.status != "Missing"] != []
        )

    def same_punches(self, other: PersonRaceResult) -> bool:
        return (
            self.punched_start_time == other.punched_start_time
            and self.punched_finish_time == other.punched_finish_time
            and [
                (p.control_code, p.punch_time)
                for p in self.split_times
                if p.status != "Missing"
            ]
            == [
                (p.control_code, p.punch_time)
                for p in other.split_times
                if p.status != "Missing"
            ]
        )

    def voided_legs(self) -> List[str]:
        voided_legs = []
        c1 = "S"
        for split_time in [s for s in self.split_times if s.status != "Additional"]:
            c2 = split_time.control_code
            if split_time.leg_voided and f"{c1}-{c2}" not in voided_legs:
                voided_legs.append(f"{c1}-{c2}")
            c1 = c2
        c2 = "F"
        if self.last_leg_voided and f"{c1}-{c2}" not in voided_legs:
            voided_legs.append(f"{c1}-{c2}")
        return voided_legs

    def compute_result(
        self,
        controls: List[str],
        class_params: ClassParams,
        start_time: Optional[datetime] = None,
        year: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> None:
        #
        # If list of controls is empty and result is not inactive or finished, no compution is done.
        # In all other cases a new result is computed, but:
        #
        # - if old status is disqualified the new status is disqualified
        # - if old status is inactive and no controls are punched the new status is inactive
        # - if old status is didnotstart and no controls are punched the new status is didnotstart
        # - if list of controls is empty and type is standard or net the new status is finished
        # - if list of controls is empty and type is score the new status is ok
        #

        # if list of controls is empty and result is not inactive or finished,
        # no compution is done
        if controls == [] and self.status not in [
            ResultStatus.INACTIVE,
            ResultStatus.FINISHED,
        ]:
            return

        # remove missing controls and reset results
        old_status = self.status
        split_times = [s for s in self.split_times if s.status != "Missing"]
        self.time = None
        self.status = ResultStatus.INACTIVE
        self.extensions = {}
        self.last_leg_voided = False
        for s in self.split_times:
            s.leg_voided = False

        # compute handicap factor
        handicap_factor = None
        if class_params.apply_handicap_rule:
            # use year of finish time to compute the age of the competitor
            h = handicap.Handicap()
            if self.punched_finish_time is not None and year is not None:
                handicap_factor = h.factor(
                    female=gender == "F", year=self.punched_finish_time.year - year
                )
            else:
                handicap_factor = h.factor(female=gender == "F", year=None)

        # compute start time
        if class_params.using_start_control == "yes":
            self.start_time = self.punched_start_time
        else:
            if (
                class_params.using_start_control == "if_punched"
                and self.punched_start_time is not None
            ):
                self.start_time = self.punched_start_time
            elif start_time is not None:
                self.start_time = start_time
            else:
                self.start_time = class_params.mass_start

        mp = self.start_time is None

        # compute finish time
        self.finish_time = self.punched_finish_time

        penalties_controls = 0
        if class_params.otype == "net":
            # controls can be visited in arbitrary order
            control_codes = controls.copy()
            self.split_times = split_times
            for p in self.split_times:
                if p.control_code in control_codes:
                    p.status = "OK"
                    p.recalculate_time(start_time=self.start_time)
                    control_codes = [c for c in control_codes if c != p.control_code]
                else:
                    p.status = "Additional"
                    p.recalculate_time(start_time=self.start_time)

            for control_code in control_codes:
                self.split_times.append(
                    SplitTime(control_code=control_code, status="Missing")
                )
                if class_params.penalty_controls is not None:
                    penalties_controls += class_params.penalty_controls
                else:
                    mp = True

        elif class_params.otype == "score":
            score_controls = 0
            # controls can be visited in arbitrary order
            control_codes = controls.copy()
            self.split_times = split_times
            for p in self.split_times:
                if p.control_code in control_codes:
                    p.status = "OK"
                    score_controls += 1
                    p.recalculate_time(start_time=self.start_time)
                    control_codes = [c for c in control_codes if c != p.control_code]
                else:
                    p.status = "Additional"
                    p.recalculate_time(start_time=self.start_time)

            for control_code in control_codes:
                self.split_times.append(
                    SplitTime(control_code=control_code, status="Missing")
                )

        else:
            # controls must be visited in the correct order
            self.split_times = []
            for control in controls:
                for i, p in enumerate(split_times):
                    if control == p.control_code:
                        for k in range(i):
                            p0 = split_times.pop(0)
                            p0.status = "Additional"
                            p0.recalculate_time(start_time=self.start_time)
                            self.split_times.append(p0)
                        p0 = split_times.pop(0)
                        p0.status = "OK"
                        p0.recalculate_time(start_time=self.start_time)
                        self.split_times.append(p0)
                        break
                else:
                    self.split_times.append(
                        SplitTime(control_code=control, status="Missing")
                    )
                    if class_params.penalty_controls is not None:
                        penalties_controls += class_params.penalty_controls
                    else:
                        mp = True

            for p in split_times:
                p.status = "Additional"
                p.recalculate_time(start_time=self.start_time)
                self.split_times.append(p)

        # compute result status
        # - if old status is disqualified the new status is disqualified
        # - if old status is inactive and no controls are punched the new status is inactive
        # - if old status is didnotstart and no controls are punched the new status is didnotstart
        # - if list of controls is empty and type is standard or net the new status is finished
        # - if list of controls is empty and type is score the new status is ok
        if old_status == ResultStatus.DISQUALIFIED:
            self.status = ResultStatus.DISQUALIFIED
        elif old_status == ResultStatus.INACTIVE and not self.has_punches():
            self.status = ResultStatus.INACTIVE
        elif old_status == ResultStatus.DID_NOT_START and not self.has_punches():
            self.status = ResultStatus.DID_NOT_START
        elif controls == [] and class_params.otype != "score":
            self.status = ResultStatus.FINISHED
        elif self.finish_time is None:
            self.status = ResultStatus.DID_NOT_FINISH
        else:
            # result status is DidNotFinish if the last three stations are missing
            missing = 0
            for p in reversed(self.split_times):
                if p.status == "OK":
                    break
                elif p.status == "Missing":
                    missing += 1
            if (
                class_params.otype == "standard"
                and class_params.penalty_overtime is None
                and missing >= 3
            ):
                self.status = ResultStatus.DID_NOT_FINISH
            else:
                self.status = ResultStatus.MISSING_PUNCH if mp else ResultStatus.OK

        # compute running time
        if self.start_time is not None and self.finish_time is not None:
            self.time = int((self.finish_time - self.start_time).total_seconds())

        # handle voided legs
        if class_params.otype == "standard" and class_params.voided_legs:
            # mark voided legs
            c1 = "S"
            for split_time in [s for s in self.split_times if s.status != "Additional"]:
                c2 = split_time.control_code
                if (c1, c2) in class_params.voided_legs:
                    split_time.leg_voided = True
                c1 = c2
            c2 = "F"
            if (c1, c2) in class_params.voided_legs:
                self.last_leg_voided = True

            # subtract time of voided legs from running time
            if self.time is not None:
                t1 = 0
                for split_time in [
                    s for s in self.split_times if s.status != "Additional"
                ]:
                    t2 = split_time.time
                    if split_time.leg_voided and t2 is not None and t1 is not None:
                        self.time -= t2 - t1
                    t1 = t2
                if self.last_leg_voided and t2 is not None:
                    self.time -= (
                        int((self.finish_time - self.start_time).total_seconds()) - t1
                    )

        if class_params.otype == "score":
            self.extensions["score_controls"] = score_controls

            # compute score for overtime
            if self.time is not None:
                score_overtime = 0
                overtime = self.time
                while overtime > class_params.time_limit:
                    overtime -= 60
                    score_overtime -= 1
                self.extensions["score_overtime"] = score_overtime

                # compute total score
                if class_params.apply_handicap_rule:
                    self.extensions["factor"] = handicap_factor
                    score = score_controls / handicap_factor + score_overtime
                else:
                    score = score_controls + score_overtime
                self.extensions["score"] = score
            else:
                self.extensions["score_overtime"] = None
                self.extensions["score"] = None

        else:
            # modify status if running time is to high
            if (
                class_params.time_limit is not None
                and class_params.penalty_overtime is None
                and self.time is not None
                and class_params.time_limit < self.time
            ):
                self.status = ResultStatus.OVER_TIME

            # modify result taking into account penalties and handicap
            if (
                class_params.penalty_controls is not None
                or class_params.penalty_overtime is not None
                or class_params.apply_handicap_rule
            ):
                # save running time if time will be modified
                self.extensions["running_time"] = self.time

                # compute penalties for overtime
                if (
                    class_params.time_limit is not None
                    and class_params.penalty_overtime is not None
                    and self.time is not None
                ):
                    # compute penalty for overtime
                    penalties_overtime = 0
                    overtime = self.time
                    while overtime > class_params.time_limit:
                        overtime -= 60
                        penalties_overtime += class_params.penalty_overtime
                    self.extensions["penalties_overtime"] = penalties_overtime
                    self.time += penalties_overtime

                # add penalties for missing controls
                if class_params.penalty_controls is not None and self.time is not None:
                    self.extensions["penalties_controls"] = penalties_controls
                    self.time += penalties_controls

                # compute total time using handicap
                if class_params.apply_handicap_rule and self.time is not None:
                    self.extensions["factor"] = handicap_factor
                    self.time = int(handicap_factor * self.time)

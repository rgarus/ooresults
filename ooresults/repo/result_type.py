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
from datetime import timezone
import enum
from typing import List
from typing import Optional
from typing import Dict

import caseconverter
import fastclasses_json

from ooresults.model import handicap
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_params import VoidedLeg


class SpStatus(enum.Enum):
    """
    SplitTime status according to IOF XML 3.0:

        OK:
            Control belongs to the course and has been punched
            (either by electronical punching or pin punching).
            If the time is not available or invalid, omit the Time element.

        MISSING:
            Control belongs to the course but has not been punched.

        ADDITIONAL:
            Control does not belong to the course, but the competitor has punched it.

    """

    OK = 0
    MISSING = 1
    ADDITIONAL = 2


@fastclasses_json.dataclass_json(field_name_transform=caseconverter.camelcase)
@dataclasses.dataclass
class SplitTime:
    NO_TIME = datetime(1970, 1, 1, tzinfo=timezone.utc)

    control_code: str
    punch_time: Optional[datetime] = None
    si_punch_time: Optional[datetime] = None
    time: Optional[int] = None
    status: Optional[SpStatus] = None
    leg_voided: bool = False

    def recalculate_time(self, start_time: Optional[datetime]) -> None:
        """
        set time as difference between start_time and punch_time
        """
        if start_time is None:
            self.time = None
        elif self.punch_time is None or self.punch_time == self.NO_TIME:
            self.time = None
        else:
            diff = self.punch_time.replace(microsecond=0) - start_time.replace(
                microsecond=0
            )
            self.time = int(diff.total_seconds())


class ResultStatus(enum.Enum):
    """
    Result status according to IOF XML 3.0:

        INACTIVE:
            Has not yet started.

        ACTIVE:
            Currently on course.

        FINISHED:
            Finished but not yet validated.

        OK:
            Finished and validated.

        MISSING_PUNCH:
            Missing punch.

        DID_NOT_START:
             Did not start (in this race).

        DID_NOT_FINISHED:
            Did not finish (i.e. conciously cancelling the race after having started,
            in contrast to MissingPunch).

        OVER_TIME:
            Overtime, i.e. did not finish within the maximum time set by the organiser.

        DISQUALIFIED:
            Disqualified (for some other reason than a missing punch).

    """

    INACTIVE = 0
    ACTIVE = 1
    FINISHED = 2
    OK = 3
    MISSING_PUNCH = 4
    DID_NOT_START = 5
    DID_NOT_FINISH = 6
    OVER_TIME = 7
    DISQUALIFIED = 8


@fastclasses_json.dataclass_json(field_name_transform=caseconverter.camelcase)
@dataclasses.dataclass
class PersonRaceResult:
    status: ResultStatus = ResultStatus.INACTIVE
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    punched_clear_time: Optional[datetime] = None
    punched_check_time: Optional[datetime] = None
    punched_start_time: Optional[datetime] = None
    punched_finish_time: Optional[datetime] = None
    si_punched_start_time: Optional[datetime] = None
    si_punched_finish_time: Optional[datetime] = None
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

    def has_punches(self) -> bool:
        return (
            self.punched_start_time is not None
            or self.punched_finish_time is not None
            or [p for p in self.split_times if p.status != SpStatus.MISSING]
        )

    def same_punches(self, other: PersonRaceResult) -> bool:
        return (
            self.punched_start_time == other.punched_start_time
            and self.punched_finish_time == other.punched_finish_time
            and [
                (p.control_code, p.punch_time)
                for p in self.split_times
                if p.status != SpStatus.MISSING
            ]
            == [
                (p.control_code, p.punch_time)
                for p in other.split_times
                if p.status != SpStatus.MISSING
            ]
        )

    def same_si_punches(self, other: PersonRaceResult) -> bool:
        return (
            self.si_punched_start_time == other.si_punched_start_time
            and self.si_punched_finish_time == other.si_punched_finish_time
            and [
                (p.control_code, p.si_punch_time)
                for p in self.split_times
                if p.si_punch_time is not None
            ]
            == [
                (p.control_code, p.si_punch_time)
                for p in other.split_times
                if p.si_punch_time is not None
            ]
        )

    def voided_legs(self) -> List[str]:
        voided_legs = []
        c1 = "S"
        for split_time in [
            s for s in self.split_times if s.status in [SpStatus.OK, SpStatus.MISSING]
        ]:
            c2 = split_time.control_code
            if split_time.leg_voided and f"{c1}-{c2}" not in voided_legs:
                voided_legs.append(f"{c1}-{c2}")
            c1 = c2
        c2 = "F"
        if self.last_leg_voided and f"{c1}-{c2}" not in voided_legs:
            voided_legs.append(f"{c1}-{c2}")
        return voided_legs

    def reset(self) -> None:
        self.status = ResultStatus.FINISHED
        self.punched_start_time = self.si_punched_start_time
        self.punched_finish_time = self.si_punched_finish_time
        for s in self.split_times:
            s.punch_time = s.si_punch_time
            s.status = SpStatus.ADDITIONAL
        self.split_times = [s for s in self.split_times if s.si_punch_time is not None]

    def compute_result(
        self,
        controls: List[str],
        class_params: ClassParams,
        start_time: Optional[datetime] = None,
        year: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> None:
        #
        # If list of controls is empty and result is not inactive. active or finished,
        # no compution is done. In all other cases a new result is computed, but:
        #
        # - if old status is disqualified the new status is disqualified
        # - if old status is overtime the new status is overtime
        # - if olf status is didnotfinish and computed result is not ok the new status is didnotfinish
        # - if old status is inactive and no controls are punched the new status is inactive
        # - if old status is didnotstart and no controls are punched the new status is didnotstart
        # - if list of controls is empty and type is standard or net the new status is finished
        # - if list of controls is empty and type is score the new status is ok
        #

        # if list of controls is empty and result is not inactive or finished,
        # no compution is done
        if controls == [] and self.status not in [
            ResultStatus.INACTIVE,
            ResultStatus.ACTIVE,
            ResultStatus.FINISHED,
        ]:
            return

        # remove missing controls and reset results
        old_status = self.status
        split_times = [
            s
            for s in self.split_times
            if s.punch_time is not None or s.si_punch_time is not None
        ]
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

        missing_punch = self.start_time is None

        # compute finish time
        self.finish_time = self.punched_finish_time

        penalties_controls = 0
        if class_params.otype == "net":
            # controls can be visited in arbitrary order
            control_codes = controls.copy()
            self.split_times = split_times
            for p in self.split_times:
                if p.control_code in control_codes and p.punch_time is not None:
                    p.status = SpStatus.OK
                    control_codes = [c for c in control_codes if c != p.control_code]
                else:
                    if p.punch_time is not None:
                        p.status = SpStatus.ADDITIONAL
                    else:
                        p.status = None
                p.recalculate_time(start_time=self.start_time)

            for control_code in control_codes:
                # reuse a removed split time as missing split time
                for p in self.split_times:
                    if control_code == p.control_code:
                        p.status = SpStatus.MISSING
                        break
                else:
                    self.split_times.append(
                        SplitTime(control_code=control_code, status=SpStatus.MISSING)
                    )
                if class_params.penalty_controls is not None:
                    penalties_controls += class_params.penalty_controls
                else:
                    missing_punch = True

        elif class_params.otype == "score":
            score_controls = 0
            # controls can be visited in arbitrary order
            control_codes = controls.copy()
            self.split_times = split_times
            for p in self.split_times:
                if p.control_code in control_codes and p.punch_time is not None:
                    p.status = SpStatus.OK
                    score_controls += 1
                    control_codes = [c for c in control_codes if c != p.control_code]
                else:
                    if p.punch_time is not None:
                        p.status = SpStatus.ADDITIONAL
                    else:
                        p.status = None
                p.recalculate_time(start_time=self.start_time)

            for control_code in control_codes:
                # reuse a removed split time as missing split time
                for p in self.split_times:
                    if control_code == p.control_code:
                        p.status = SpStatus.MISSING
                        break
                else:
                    self.split_times.append(
                        SplitTime(control_code=control_code, status=SpStatus.MISSING)
                    )

        else:
            # controls must be visited in the correct order
            self.split_times = []
            for control in controls:
                while split_times and split_times[0].punch_time is None:
                    p0 = split_times.pop(0)
                    p0.status = None
                    p0.recalculate_time(start_time=self.start_time)
                    self.split_times.append(p0)

                for i, p in enumerate(split_times):
                    if control == p.control_code and p.punch_time is not None:
                        for k in range(i):
                            p0 = split_times.pop(0)
                            if p0.punch_time is not None:
                                p0.status = SpStatus.ADDITIONAL
                            else:
                                p0.status = None
                            p0.recalculate_time(start_time=self.start_time)
                            self.split_times.append(p0)
                        p0 = split_times.pop(0)
                        p0.status = SpStatus.OK
                        p0.recalculate_time(start_time=self.start_time)
                        self.split_times.append(p0)
                        break
                else:
                    # reuse a removed split time as missing split time
                    candidates = []
                    for p in reversed(self.split_times):
                        if p.status is None:
                            candidates.append(p)
                        else:
                            break
                    for p in reversed(candidates):
                        if control == p.control_code:
                            p.status = SpStatus.MISSING
                            break
                    else:
                        self.split_times.append(
                            SplitTime(control_code=control, status=SpStatus.MISSING)
                        )
                    if class_params.penalty_controls is not None:
                        penalties_controls += class_params.penalty_controls
                    else:
                        missing_punch = True

            for p in split_times:
                if p.punch_time is not None:
                    p.status = SpStatus.ADDITIONAL
                else:
                    p.status = None
                p.recalculate_time(start_time=self.start_time)
                self.split_times.append(p)

        # compute result status
        # - if no controls are punched the new status is inactive
        # - if list of controls is empty the new status is finished
        # - if controls punched but no finish time the new status is did_not_finish
        # - if run time greater time limit the new status is overtime
        # - if controls punched but some missing the new status is missing_punch

        if not self.has_punches():
            self.status = ResultStatus.INACTIVE
        elif controls == []:
            self.status = ResultStatus.FINISHED
        elif self.finish_time is None:
            self.status = ResultStatus.DID_NOT_FINISH
        elif missing_punch:
            self.status = ResultStatus.MISSING_PUNCH
        else:
            self.status = ResultStatus.OK

        # compute running time
        if self.start_time is not None and self.finish_time is not None:
            self.time = int((self.finish_time - self.start_time).total_seconds())

        # handle voided legs
        if class_params.otype == "standard" and class_params.voided_legs:
            # mark voided legs
            c1 = "S"
            for split_time in [
                s
                for s in self.split_times
                if s.status in (SpStatus.OK, SpStatus.MISSING)
            ]:
                c2 = split_time.control_code
                if VoidedLeg(c1, c2) in class_params.voided_legs:
                    split_time.leg_voided = True
                c1 = c2
            c2 = "F"
            if VoidedLeg(c1, c2) in class_params.voided_legs:
                self.last_leg_voided = True

            # subtract time of voided legs from running time
            # for example (controls 101-102-103):
            #
            # voidedLeg = 101-102,         times 2:00-3:00-4:00 -> subtract 60 sec
            # voidedLeg = 102-103,         times 2:00-3:00-4:00 -> subtract 60 sec
            # voidedLeg = 101-102,102-103, times 2:00-3:00-4:00 -> subtract 120 sec
            # voidedLeg = 101-102,         times 2:00-ok-4:00   -> not possible
            # voidedLeg = 102-103,         times 2:00-ok-4:00   -> not possible
            # voidedLeg = 101-102,102-103, times 2:00-ok-4:00   -> subtract 120 sec
            # voidedLeg = 101-102,102-103, times ok-3:00-4:00   -> subtract 60 sec
            #
            if self.time is not None:
                t1 = 0
                for split_time in [
                    s
                    for s in self.split_times
                    if s.status in (SpStatus.OK, SpStatus.MISSING)
                ]:
                    t2 = split_time.time
                    if split_time.leg_voided:
                        if t2 is not None:
                            if t1 is not None:
                                self.time -= t2 - t1
                            t1 = t2
                    else:
                        t1 = t2
                if self.last_leg_voided and t1 is not None:
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
            # modify status if running time is too high
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

        # update result status
        # - disqualified always
        # - over_time always
        # - did_not_finish only if computed status is not ok or over_time
        # - did_not_start only if computed status is not ok, over_time, missing_punch, did_not_finish or finished
        # - inactive only if computed status is not ok, over_time, missing_punch, did_not_finish or finished
        # - active only if computed status is not ok, over_time, missing_punch, did_not_finish or finished

        if old_status in (
            ResultStatus.DISQUALIFIED,
            ResultStatus.OVER_TIME,
        ):
            self.status = old_status
        elif old_status == ResultStatus.DID_NOT_FINISH and self.status not in (
            ResultStatus.OK,
            ResultStatus.OVER_TIME,
        ):
            self.status = old_status
        elif old_status in (
            ResultStatus.DID_NOT_START,
            ResultStatus.INACTIVE,
            ResultStatus.ACTIVE,
        ) and self.status not in (
            ResultStatus.OK,
            ResultStatus.OVER_TIME,
            ResultStatus.MISSING_PUNCH,
            ResultStatus.DID_NOT_FINISH,
            ResultStatus.FINISHED,
        ):
            self.status = old_status


@dataclasses.dataclass
class CardReaderMessage:
    entry_type: str
    entry_time: datetime
    control_card: Optional[str]
    result: Optional[PersonRaceResult]

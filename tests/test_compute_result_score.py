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


from datetime import datetime
from datetime import timezone

import pytest

from ooresults.model import handicap
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.class_params import ClassParams


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.OK),
        (ResultStatus.ACTIVE, ResultStatus.OK),
        (ResultStatus.FINISHED, ResultStatus.OK),
        (ResultStatus.OK, ResultStatus.OK),
        (ResultStatus.MISSING_PUNCH, ResultStatus.OK),
        (ResultStatus.DID_NOT_START, ResultStatus.OK),
        (ResultStatus.DID_NOT_FINISH, ResultStatus.OK),
        (ResultStatus.OVER_TIME, ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED, ResultStatus.DISQUALIFIED),
    ],
)
@pytest.mark.parametrize("time_limit, score_overtime", [(60, -2), (120, -1), (180, 0)])
def test_compute_result_status_ok(
    time_limit: int,
    score_overtime: int,
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 41, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="103", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="101", punch_time=c3, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(otype="score", time_limit=time_limit)

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
        extensions={
            "score_controls": 3,
            "score_overtime": score_overtime,
            "score": 3 + score_overtime,
        },
        split_times=[
            SplitTime(
                control_code="103", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status=SpStatus.OK
            ),
            SplitTime(
                control_code="101", punch_time=c3, time=t(s1, c3), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize(
    "status_old,status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.OK),
        (ResultStatus.ACTIVE, ResultStatus.OK),
        (ResultStatus.FINISHED, ResultStatus.OK),
        (ResultStatus.OK, ResultStatus.OK),
        (ResultStatus.MISSING_PUNCH, ResultStatus.OK),
        (ResultStatus.DID_NOT_START, ResultStatus.OK),
        (ResultStatus.DID_NOT_FINISH, ResultStatus.OK),
        (ResultStatus.OVER_TIME, ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED, ResultStatus.DISQUALIFIED),
    ],
)
def test_compute_result_status_with_missing_punches(
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103", "104"]
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c3, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(otype="score", time_limit=60)

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
        extensions={
            "score_controls": 2,
            "score_overtime": 0,
            "score": 2,
        },
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=None, time=None, status=SpStatus.MISSING
            ),
            SplitTime(
                control_code="104", punch_time=None, time=None, status=SpStatus.MISSING
            ),
        ],
    )


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.OK),
        (ResultStatus.ACTIVE, ResultStatus.OK),
        (ResultStatus.FINISHED, ResultStatus.OK),
        (ResultStatus.OK, ResultStatus.OK),
        (ResultStatus.MISSING_PUNCH, ResultStatus.OK),
        (ResultStatus.DID_NOT_START, ResultStatus.OK),
        (ResultStatus.DID_NOT_FINISH, ResultStatus.OK),
        (ResultStatus.OVER_TIME, ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED, ResultStatus.DISQUALIFIED),
    ],
)
def test_compute_result_status_ok_with_additionals(
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    c4 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)
    c5 = datetime(2015, 1, 1, 12, 39, 9, tzinfo=timezone.utc)
    c6 = datetime(2015, 1, 1, 12, 39, 11, tzinfo=timezone.utc)
    c7 = datetime(2015, 1, 1, 12, 39, 13, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="105", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="101", punch_time=c3, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c4, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c5, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="101", punch_time=c6, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="104", punch_time=c7, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(otype="score", time_limit=60)

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
        extensions={
            "score_controls": 3,
            "score_overtime": 0,
            "score": 3,
        },
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="105",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="101",
                punch_time=c3,
                time=t(s1, c3),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="103", punch_time=c4, time=t(s1, c4), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=c5, time=t(s1, c5), status=SpStatus.OK
            ),
            SplitTime(
                control_code="101",
                punch_time=c6,
                time=t(s1, c6),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="104",
                punch_time=c7,
                time=t(s1, c7),
                status=SpStatus.ADDITIONAL,
            ),
        ],
    )


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.OK),
        (ResultStatus.ACTIVE, ResultStatus.OK),
        (ResultStatus.FINISHED, ResultStatus.OK),
        (ResultStatus.OK, ResultStatus.OK),
        (ResultStatus.MISSING_PUNCH, ResultStatus.OK),
        (ResultStatus.DID_NOT_START, ResultStatus.OK),
        (ResultStatus.DID_NOT_FINISH, ResultStatus.OK),
        (ResultStatus.OVER_TIME, ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED, ResultStatus.DISQUALIFIED),
    ],
)
def test_compute_result_with_unknown_punch_times(
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = SplitTime.NO_TIME
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = SplitTime.NO_TIME
    c4 = SplitTime.NO_TIME
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="104", punch_time=c3, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c4, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(otype="score", time_limit=60)

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
        extensions={
            "score_controls": 3,
            "score_overtime": 0,
            "score": 3,
        },
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                time=None,
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="104",
                punch_time=c3,
                time=None,
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="103",
                punch_time=c4,
                time=None,
                status=SpStatus.OK,
            ),
        ],
    )


@pytest.mark.parametrize("time_limit, score_overtime", [(60, -2), (120, -1), (180, 0)])
@pytest.mark.parametrize(
    "female, year_of_birth", [(True, 2000), (True, 1981), (False, 1941)]
)
def test_compute_handicap_ok(time_limit, score_overtime, female, year_of_birth):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 41, 7, tzinfo=timezone.utc)

    controls = ["101"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(
        otype="score", time_limit=time_limit, apply_handicap_rule=True
    )

    result.compute_result(
        controls=controls,
        class_params=class_params,
        year=year_of_birth,
        gender="F" if female else "M",
    )
    h = handicap.Handicap()

    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        extensions={
            "factor": h.factor(female=female, year=f1.year - year_of_birth),
            "score_controls": 1,
            "score_overtime": score_overtime,
            "score": 1 / result.extensions["factor"] + score_overtime,
        },
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize(
    "female, year_of_birth", [(True, 2000), (True, 1981), (False, 1941)]
)
def test_compute_handicap_mp(female, year_of_birth):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[],
    )
    class_params = ClassParams(otype="score", time_limit=60, apply_handicap_rule=True)

    result.compute_result(
        controls=controls,
        class_params=class_params,
        year=year_of_birth,
        gender="F" if female else "M",
    )
    h = handicap.Handicap()

    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        extensions={
            "factor": h.factor(female=female, year=f1.year - year_of_birth),
            "score_controls": 0,
            "score_overtime": 0,
            "score": 0,
        },
        split_times=[
            SplitTime(
                control_code="101", punch_time=None, time=None, status=SpStatus.MISSING
            ),
        ],
    )

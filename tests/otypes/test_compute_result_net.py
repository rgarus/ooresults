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

from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.result_type import SpStatus


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
def test_compute_result_status_ok(
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

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
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
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
        (ResultStatus.INACTIVE, ResultStatus.MISSING_PUNCH),
        (ResultStatus.ACTIVE, ResultStatus.MISSING_PUNCH),
        (ResultStatus.FINISHED, ResultStatus.MISSING_PUNCH),
        (ResultStatus.OK, ResultStatus.MISSING_PUNCH),
        (ResultStatus.MISSING_PUNCH, ResultStatus.MISSING_PUNCH),
        (ResultStatus.DID_NOT_START, ResultStatus.MISSING_PUNCH),
        (ResultStatus.DID_NOT_FINISH, ResultStatus.DID_NOT_FINISH),
        (ResultStatus.OVER_TIME, ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED, ResultStatus.DISQUALIFIED),
    ],
)
def test_compute_result_status_mispunched(
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
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
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
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
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
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=status_new,
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

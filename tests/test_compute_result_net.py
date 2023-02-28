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


from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.class_params import ClassParams


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


def test_compute_result_status_ok():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="103", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="101", punch_time=c3, status="Additional"),
        ],
    )
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
    assert len(result.split_times) == 3
    assert result.split_times[0] == SplitTime(
        control_code="103", punch_time=c1, time=t(s1, c1), status="OK"
    )
    assert result.split_times[1] == SplitTime(
        control_code="102", punch_time=c2, time=t(s1, c2), status="OK"
    )
    assert result.split_times[2] == SplitTime(
        control_code="101", punch_time=c3, time=t(s1, c3), status="OK"
    )


def test_compute_result_status_mispunched():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103", "104"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.MISSING_PUNCH
    assert len(result.split_times) == 4
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=t(s1, c1), status="OK"
    )
    assert result.split_times[1] == SplitTime(
        control_code="103", punch_time=c3, time=t(s1, c3), status="OK"
    )
    assert result.split_times[2] == SplitTime(
        control_code="102", punch_time=None, time=None, status="Missing"
    )
    assert result.split_times[3] == SplitTime(
        control_code="104", punch_time=None, time=None, status="Missing"
    )


def test_compute_result_status_ok_with_additionals():
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
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="105", punch_time=c2, status="Additional"),
            SplitTime(control_code="101", punch_time=c3, status="Additional"),
            SplitTime(control_code="103", punch_time=c4, status="Additional"),
            SplitTime(control_code="102", punch_time=c5, status="Additional"),
            SplitTime(control_code="101", punch_time=c6, status="Additional"),
            SplitTime(control_code="104", punch_time=c7, status="Additional"),
        ],
    )
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
    assert len(result.split_times) == 7
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=t(s1, c1), status="OK"
    )
    assert result.split_times[1] == SplitTime(
        control_code="105", punch_time=c2, time=t(s1, c2), status="Additional"
    )
    assert result.split_times[2] == SplitTime(
        control_code="101", punch_time=c3, time=t(s1, c3), status="Additional"
    )
    assert result.split_times[3] == SplitTime(
        control_code="103", punch_time=c4, time=t(s1, c4), status="OK"
    )
    assert result.split_times[4] == SplitTime(
        control_code="102", punch_time=c5, time=t(s1, c5), status="OK"
    )
    assert result.split_times[5] == SplitTime(
        control_code="101", punch_time=c6, time=t(s1, c6), status="Additional"
    )
    assert result.split_times[6] == SplitTime(
        control_code="104", punch_time=c7, time=t(s1, c7), status="Additional"
    )


def test_compute_result_status_last_three_stations_missing():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 11, tzinfo=timezone.utc)
    c4 = datetime(2015, 1, 1, 12, 39, 13, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    controls = ["101", "102", "103", "104", "105"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="106", punch_time=c3, status="Additional"),
            SplitTime(control_code="107", punch_time=c4, status="Additional"),
        ],
    )
    class_params = ClassParams(otype="net")

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.MISSING_PUNCH
    assert len(result.split_times) == 7
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=t(s1, c1), status="OK"
    )
    assert result.split_times[1] == SplitTime(
        control_code="102", punch_time=c2, time=t(s1, c2), status="OK"
    )
    assert result.split_times[2] == SplitTime(
        control_code="106", punch_time=c3, time=t(s1, c3), status="Additional"
    )
    assert result.split_times[3] == SplitTime(
        control_code="107", punch_time=c4, time=t(s1, c4), status="Additional"
    )
    assert result.split_times[4] == SplitTime(
        control_code="103", punch_time=None, time=None, status="Missing"
    )
    assert result.split_times[5] == SplitTime(
        control_code="104", punch_time=None, time=None, status="Missing"
    )
    assert result.split_times[6] == SplitTime(
        control_code="105", punch_time=None, time=None, status="Missing"
    )

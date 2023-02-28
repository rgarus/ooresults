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

from ooresults.handler import handicap
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.class_params import ClassParams


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


@pytest.mark.parametrize("time_limit, score_overtime", [(60, -2), (120, -1), (180, 0)])
def test_compute_result_status_ok(time_limit, score_overtime):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 41, 7, tzinfo=timezone.utc)

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
    class_params = ClassParams(otype="score", time_limit=time_limit)

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
    assert len(result.extensions) == 3
    assert result.extensions["score_controls"] == 3
    assert result.extensions["score_overtime"] == score_overtime
    assert result.extensions["score"] == 3 + score_overtime


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
    class_params = ClassParams(otype="score", time_limit=60)

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
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
    assert len(result.extensions) == 3
    assert result.extensions["score_controls"] == 2
    assert result.extensions["score_overtime"] == 0
    assert result.extensions["score"] == 2


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
    class_params = ClassParams(otype="score", time_limit=60)

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
    assert len(result.extensions) == 3
    assert result.extensions["score_controls"] == 3
    assert result.extensions["score_overtime"] == 0
    assert result.extensions["score"] == 3


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
    class_params = ClassParams(otype="score", time_limit=60)

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
    assert len(result.extensions) == 3
    assert result.extensions["score_controls"] == 2
    assert result.extensions["score_overtime"] == 0
    assert result.extensions["score"] == 2


def test_given_no_controls_but_punches_when_compute_results_then_status_is_ok():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    controls = []
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
        ],
    )
    class_params = ClassParams(otype="score", time_limit=60)

    result.compute_result(controls=controls, class_params=class_params)
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
    assert len(result.split_times) == 2
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
    )
    assert result.split_times[1] == SplitTime(
        control_code="102", punch_time=c2, time=t(s1, c2), status="Additional"
    )
    assert len(result.extensions) == 3
    assert result.extensions["score_controls"] == 0
    assert result.extensions["score_overtime"] == 0
    assert result.extensions["score"] == 0


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
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
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
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.extensions["factor"] == h.factor(
        female=female, year=f1.year - year_of_birth
    )
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
    assert len(result.split_times) == 1
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=t(s1, c1), status="OK"
    )
    assert len(result.extensions) == 4
    assert result.extensions["score_controls"] == 1
    assert result.extensions["score_overtime"] == score_overtime
    assert (
        result.extensions["score"] == 1 / result.extensions["factor"] + score_overtime
    )


@pytest.mark.parametrize(
    "female, year_of_birth", [(True, 2000), (True, 1981), (False, 1941)]
)
def test_compute_handicap_mp(female, year_of_birth):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
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
    assert result.start_time == s1
    assert result.punched_start_time == s1
    assert result.finish_time == f1
    assert result.punched_finish_time == f1
    assert result.extensions["factor"] == h.factor(
        female=female, year=f1.year - year_of_birth
    )
    assert result.time == int((f1 - s1).total_seconds())
    assert result.status == ResultStatus.OK
    assert len(result.split_times) == 1
    assert result.split_times[0] == SplitTime(
        control_code="101", punch_time=None, time=None, status="Missing"
    )
    assert len(result.extensions) == 4
    assert result.extensions["score_controls"] == 0
    assert result.extensions["score_overtime"] == 0
    assert result.extensions["score"] == 0

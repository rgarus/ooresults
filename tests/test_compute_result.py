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


import copy
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
    "status",
    [
        (ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED),
    ],
)
@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_result_status_is_otl_dsq_when_compute_result_then_result_status_is_not_changed(
    otype: str,
    status: ResultStatus,
):
    time_limit = 60 if otype == "score" else None
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=status,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c3, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 3,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=f1,
        punched_finish_time=f1,
        time=None,
        status=status,
        extensions=extensions,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=None, status=SpStatus.OK),
            SplitTime(control_code="102", punch_time=c2, time=None, status=SpStatus.OK),
            SplitTime(control_code="103", punch_time=c3, time=None, status=SpStatus.OK),
        ],
    )


@pytest.mark.parametrize(
    "status",
    [
        (ResultStatus.OK),
        (ResultStatus.MISSING_PUNCH),
        (ResultStatus.DID_NOT_START),
        (ResultStatus.DID_NOT_FINISH),
        (ResultStatus.OVER_TIME),
        (ResultStatus.DISQUALIFIED),
    ],
)
@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_no_controls_and_status_is_not_inactive_active_finished_then_result_is_not_changed(
    otype: str,
    status: ResultStatus,
):
    time_limit = 60 if otype == "score" else None
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = []
    result = PersonRaceResult(
        status=status,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
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
                time=None,
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="103",
                punch_time=None,
                time=None,
                status=SpStatus.MISSING,
            ),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    new_result = copy.deepcopy(result)
    new_result.compute_result(controls=controls, class_params=class_params)
    assert new_result == result


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.FINISHED),
        (ResultStatus.ACTIVE, ResultStatus.FINISHED),
        (ResultStatus.FINISHED, ResultStatus.FINISHED),
    ],
)
@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_no_controls_but_punches_and_status_inactive_active_finished_then_result_status_is_finished(
    otype: str,
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    time_limit = 60 if otype == "score" else None
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = []
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
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
                time=None,
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="103",
                punch_time=None,
                time=None,
                status=SpStatus.MISSING,
            ),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 0,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        status=status_new,
        punched_start_time=None,
        finish_time=f1,
        punched_finish_time=f1,
        time=None,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                time=None,
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=None,
                status=SpStatus.ADDITIONAL,
            ),
        ],
    )


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.INACTIVE),
        (ResultStatus.ACTIVE, ResultStatus.ACTIVE),
        (ResultStatus.FINISHED, ResultStatus.INACTIVE),
    ],
)
@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_no_controls_and_no_punches_and_status_inactive_active_finished_then_result_status_is_inactive_or_active(
    otype: str,
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    time_limit = 60 if otype == "score" else None

    controls = []
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=None,
        punched_finish_time=None,
        time=None,
        split_times=[],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 0,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        status=status_new,
        start_time=None,
        punched_start_time=None,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        extensions=extensions,
        split_times=[],
    )


@pytest.mark.parametrize(
    "status_old, status_new",
    [
        (ResultStatus.INACTIVE, ResultStatus.INACTIVE),
        (ResultStatus.ACTIVE, ResultStatus.ACTIVE),
        (ResultStatus.DID_NOT_START, ResultStatus.DID_NOT_START),
    ],
)
@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_no_punches_and_status_inactive_active_dns_when_compute_result_then_status_is_not_changed(
    otype: str,
    status_old: ResultStatus,
    status_new: ResultStatus,
):
    time_limit = 60 if otype == "score" else None

    controls = ["101", "102"]
    result = PersonRaceResult(
        status=status_old,
        punched_start_time=None,
        punched_finish_time=None,
        time=None,
        split_times=[],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 0,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        status=status_new,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=None, time=None, status=SpStatus.MISSING
            ),
            SplitTime(
                control_code="102", punch_time=None, time=None, status=SpStatus.MISSING
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_status_no_start_time(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c3, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 3,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=f1,
        punched_finish_time=f1,
        time=None,
        status=ResultStatus.MISSING_PUNCH,
        extensions=extensions,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=None, status=SpStatus.OK),
            SplitTime(control_code="102", punch_time=c2, time=None, status=SpStatus.OK),
            SplitTime(control_code="103", punch_time=c3, time=None, status=SpStatus.OK),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_status_no_finish_time(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    controls = ["101", "102", "103"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=s1,
        punched_finish_time=None,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=c3, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 3,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        status=ResultStatus.DID_NOT_FINISH,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status=SpStatus.OK
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_given_no_punches_and_status_is_inactive_when_compute_result_then_new_status_is_inactive(
    otype: str,
):
    time_limit = 60 if otype == "score" else None

    controls = []
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=None,
        punched_finish_time=None,
        time=None,
        split_times=[],
    )
    class_params = ClassParams(
        otype=otype,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 0,
            "score_overtime": None,
            "score": None,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        status=ResultStatus.INACTIVE,
        extensions=extensions,
        split_times=[],
    )


@pytest.mark.parametrize("otype", ["standard", "net"])
def test_given_no_controls_but_punches_when_compute_result_then_status_is_finished(
    otype: str,
):
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
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=c2, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(otype=otype)

    result.compute_result(controls=controls, class_params=class_params)
    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.FINISHED,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                time=t(s1, c1),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.ADDITIONAL,
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net"])
@pytest.mark.parametrize(
    "female, year_of_birth", [(True, 2000), (True, 1981), (False, 1941)]
)
def test_compute_handicap_ok(
    otype: str,
    female: bool,
    year_of_birth: int,
):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

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
    class_params = ClassParams(otype=otype, apply_handicap_rule=True)

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
        extensions={
            "running_time": int((f1 - s1).total_seconds()),
            "factor": h.factor(female=female, year=f1.year - year_of_birth),
        },
        time=int(result.extensions["running_time"] * result.extensions["factor"]),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net"])
@pytest.mark.parametrize(
    "female, year_of_birth", [(True, 2000), (True, 1981), (False, 1941)]
)
def test_compute_handicap_mp(
    otype: str,
    female: bool,
    year_of_birth: int,
):
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
    class_params = ClassParams(otype=otype, apply_handicap_rule=True)

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
        time=int(result.extensions["running_time"] * result.extensions["factor"]),
        status=ResultStatus.MISSING_PUNCH,
        extensions={
            "running_time": int((f1 - s1).total_seconds()),
            "factor": h.factor(female=female, year=f1.year - year_of_birth),
        },
        split_times=[
            SplitTime(
                control_code="101", punch_time=None, time=None, status=SpStatus.MISSING
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_use_personal_start_time_if_using_start_control_is_no(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    p1 = datetime(2015, 1, 1, 12, 38, 50, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

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
        otype=otype,
        using_start_control="no",
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params, start_time=p1)
    if otype == "score":
        extensions = {
            "score_controls": 1,
            "score_overtime": 0,
            "score": 1,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=p1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - p1).total_seconds()),
        status=ResultStatus.OK,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(p1, c1), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_use_mass_time_if_no_personal_start_time_and_using_start_control_is_no(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    p1 = datetime(2015, 1, 1, 12, 38, 50, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

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
        otype=otype,
        using_start_control="no",
        mass_start=p1,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params)
    if otype == "score":
        extensions = {
            "score_controls": 1,
            "score_overtime": 0,
            "score": 1,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=p1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - p1).total_seconds()),
        status=ResultStatus.OK,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(p1, c1), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_use_punched_time_if_using_start_control_is_yes(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    p1 = datetime(2015, 1, 1, 12, 38, 50, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

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
        otype=otype,
        using_start_control="yes",
        mass_start=p1,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params, start_time=p1)
    if otype == "score":
        extensions = {
            "score_controls": 1,
            "score_overtime": 0,
            "score": 1,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
        ],
    )


@pytest.mark.parametrize("otype", ["standard", "net", "score"])
def test_compute_result_use_personal_start_time_if_using_start_control_is_if_punched_and_no_punch_time(
    otype: str,
):
    time_limit = 60 if otype == "score" else None
    p1 = datetime(2015, 1, 1, 12, 38, 50, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    controls = ["101"]
    result = PersonRaceResult(
        status=ResultStatus.INACTIVE,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status=SpStatus.ADDITIONAL),
        ],
    )
    class_params = ClassParams(
        otype=otype,
        using_start_control="if_punched",
        mass_start=p1,
        time_limit=time_limit,
    )

    result.compute_result(controls=controls, class_params=class_params, start_time=p1)
    if otype == "score":
        extensions = {
            "score_controls": 1,
            "score_overtime": 0,
            "score": 1,
        }
    else:
        extensions = {}

    assert result == PersonRaceResult(
        start_time=p1,
        punched_start_time=None,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - p1).total_seconds()),
        status=ResultStatus.OK,
        extensions=extensions,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(p1, c1), status=SpStatus.OK
            ),
        ],
    )

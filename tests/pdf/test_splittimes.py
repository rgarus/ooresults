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

from ooresults.pdf.splittimes import format_result
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_status_ok(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 59, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 15, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 15, 39, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
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

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("0:02", "0:02", None),
            ("20:04", "20:02", None),
            ("180:06", "160:02", None),
            ("180:08", "0:02", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "0:02", "0:02"),
            ("#(102)", "20:04", "20:02"),
            ("#(103)", "180:06", "160:02"),
            ("F", "180:08", "0:02"),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_status_mispunched(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.MISSING_PUNCH,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=None, time=None, status=SpStatus.MISSING
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status=SpStatus.OK
            ),
            SplitTime(
                control_code="104", punch_time=None, time=None, status=SpStatus.MISSING
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("0:02", "0:02", None),
            ("-----", "-----", None),
            ("0:06", "0:04", None),
            ("-----", "-----", None),
            ("0:08", "0:02", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "0:02", "0:02"),
            ("#(102)", "-----", "-----"),
            ("#(103)", "0:06", "0:04"),
            ("#(104)", "-----", "-----"),
            ("F", "0:08", "0:02"),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_compute_result_status_ok_with_additionals(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    c4 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)
    c5 = datetime(2015, 1, 1, 12, 39, 9, tzinfo=timezone.utc)
    c6 = datetime(2015, 1, 1, 12, 39, 11, tzinfo=timezone.utc)
    c7 = datetime(2015, 1, 1, 12, 39, 13, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                time=t(s1, c1),
                status=SpStatus.OK,
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
                control_code="102",
                punch_time=c4,
                time=t(s1, c4),
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="103",
                punch_time=c5,
                time=t(s1, c5),
                status=SpStatus.OK,
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

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("0:02", "0:02", None),
            ("0:08", "0:06", None),
            ("0:10", "0:02", None),
            ("0:16", "0:06", None),
            ("", "", ""),
            ("0:04", "*(105)", None),
            ("0:06", "*(101)", None),
            ("0:12", "*(101)", None),
            ("0:14", "*(104)", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "0:02", "0:02"),
            ("#(102)", "0:08", "0:06"),
            ("#(103)", "0:10", "0:02"),
            ("F", "0:16", "0:06"),
            ("", "", ""),
            ("*(105)", "0:04", ""),
            ("*(101)", "0:06", ""),
            ("*(101)", "0:12", ""),
            ("*(104)", "0:14", ""),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_si_times_changed(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 40, 1, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 43, 7, tzinfo=timezone.utc)
    si_s1 = datetime(2015, 1, 1, 12, 37, 59, tzinfo=timezone.utc)
    si_c1 = datetime(2015, 1, 1, 12, 50, 1, tzinfo=timezone.utc)
    si_c2 = datetime(2015, 1, 1, 12, 51, 3, tzinfo=timezone.utc)
    si_f1 = datetime(2015, 1, 1, 12, 53, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        si_punched_start_time=si_s1,
        punched_start_time=s1,
        finish_time=f1,
        si_punched_finish_time=si_f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.MISSING_PUNCH,
        split_times=[
            SplitTime(
                control_code="101",
                si_punch_time=si_c1,
                punch_time=c1,
                time=t(s1, c1),
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="102",
                si_punch_time=si_c2,
                punch_time=None,
                time=None,
                status=SpStatus.MISSING,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("1:02", "1:02", None),
            ("-----", "-----", None),
            ("4:08", "3:06", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "1:02", "1:02"),
            ("#(102)", "-----", "-----"),
            ("F", "4:08", "3:06"),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_unknown_punch_times(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = SplitTime.NO_TIME
    c2 = SplitTime.NO_TIME
    f1 = datetime(2015, 1, 1, 12, 43, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=None, status=SpStatus.OK),
            SplitTime(control_code="102", punch_time=c2, time=None, status=SpStatus.OK),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("ok", "", None),
            ("ok", "", None),
            ("4:08", "4:08", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "ok", ""),
            ("#(102)", "ok", ""),
            ("F", "4:08", "4:08"),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_no_start_time(standard):
    c1 = datetime(2015, 1, 1, 12, 40, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 41, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 41, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 15, 42, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=f1,
        punched_finish_time=f1,
        time=None,
        status=ResultStatus.MISSING_PUNCH,
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
                punch_time=c3,
                time=None,
                status=SpStatus.OK,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("ok", "", None),
            ("ok", "", None),
            ("ok", "", None),
            ("", "", ""),
            ("ok", "*(102)", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "ok", ""),
            ("#(103)", "ok", ""),
            ("F", "ok", ""),
            ("", "", ""),
            ("*(102)", "ok", ""),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_no_start_time_and_no_finish_time(standard):
    c1 = datetime(2015, 1, 1, 12, 40, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 41, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 41, 5, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=None,
        punched_start_time=None,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        status=ResultStatus.DID_NOT_FINISH,
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
                punch_time=c3,
                time=None,
                status=SpStatus.OK,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("ok", "", None),
            ("ok", "", None),
            ("-----", "-----", None),
            ("", "", ""),
            ("ok", "*(102)", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "ok", ""),
            ("#(103)", "ok", ""),
            ("F", "-----", "-----"),
            ("", "", ""),
            ("*(102)", "ok", ""),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_no_finish_time(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 40, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 41, 3, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=None,
        punched_finish_time=None,
        time=None,
        status=ResultStatus.DID_NOT_FINISH,
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status=SpStatus.OK
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status=SpStatus.OK
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("1:02", "1:02", None),
            ("2:04", "1:02", None),
            ("-----", "-----", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "1:02", "1:02"),
            ("#(102)", "2:04", "1:02"),
            ("F", "-----", "-----"),
        ]


@pytest.mark.parametrize("standard", [True, False])
def test_format_result_with_voided_legs(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 43, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 44, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        last_leg_voided=True,
        time=int((c2 - c1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                leg_voided=True,
                time=t(s1, c1),
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.OK,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("0:02", "[0:02]", None),
            ("4:04", "4:02", None),
            ("5:08", "[1:04]", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "0:02", "0:02"),
            ("#(102)", "4:04", "4:02"),
            ("F", "5:08", "1:04"),
        ]


def test_format_result_with_voided_leg_and_missing_punch():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 43, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 44, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        last_leg_voided=True,
        time=int((c2 - c1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                leg_voided=True,
                time=None,
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.OK,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=True))
    assert formatted_result == [
        ("ok", "", None),
        ("4:04", "4:04", None),
        ("5:08", "[1:04]", None),
    ]


def test_format_result_with_voided_leg_and_unknown_punch_time():
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = SplitTime.NO_TIME
    c2 = datetime(2015, 1, 1, 12, 43, 3, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 44, 7, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        last_leg_voided=True,
        time=int((c2 - c1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=None,
                leg_voided=True,
                time=None,
                status=SpStatus.MISSING,
            ),
            SplitTime(
                control_code="102",
                punch_time=c2,
                time=t(s1, c2),
                status=SpStatus.OK,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=True))
    assert formatted_result == [
        ("-----", "-----", None),
        ("4:04", "4:04", None),
        ("5:08", "[1:04]", None),
    ]


@pytest.mark.parametrize("standard", [True, False])
def test_compute_result_remove_unnecessary_additionals(standard):
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
    c3 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    c4 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)
    c5 = datetime(2015, 1, 1, 12, 39, 9, tzinfo=timezone.utc)
    c6 = datetime(2015, 1, 1, 12, 39, 11, tzinfo=timezone.utc)
    c7 = datetime(2015, 1, 1, 12, 39, 13, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 15, tzinfo=timezone.utc)

    result = PersonRaceResult(
        start_time=s1,
        punched_start_time=s1,
        finish_time=f1,
        punched_finish_time=f1,
        time=int((f1 - s1).total_seconds()),
        status=ResultStatus.OK,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=c1,
                time=t(s1, c1),
                status=SpStatus.OK,
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
                control_code="101",
                punch_time=c4,
                time=t(s1, c4),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="103",
                punch_time=c5,
                time=t(s1, c5),
                status=SpStatus.OK,
            ),
            SplitTime(
                control_code="103",
                punch_time=c6,
                time=t(s1, c6),
                status=SpStatus.ADDITIONAL,
            ),
            SplitTime(
                control_code="104",
                punch_time=None,
                time=None,
                status=SpStatus.MISSING,
            ),
            SplitTime(
                control_code="103",
                punch_time=c7,
                time=t(s1, c7),
                status=SpStatus.ADDITIONAL,
            ),
        ],
    )

    formatted_result = list(format_result(result=result, standard=standard))
    if standard:
        assert formatted_result == [
            ("0:02", "0:02", None),
            ("0:10", "0:08", None),
            ("-----", "-----", None),
            ("0:16", "0:06", None),
            ("", "", ""),
            ("0:04", "*(105)", None),
            ("0:06", "*(101)", None),
        ]
    else:
        assert formatted_result == [
            ("#(101)", "0:02", "0:02"),
            ("#(103)", "0:10", "0:08"),
            ("#(104)", "-----", "-----"),
            ("F", "0:16", "0:06"),
            ("", "", ""),
            ("*(105)", "0:04", ""),
            ("*(101)", "0:06", ""),
        ]

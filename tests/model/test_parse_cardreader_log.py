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
from datetime import timedelta
from datetime import timezone

import pytest
import jsonschema

from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import ResultStatus
from ooresults.handler import model


def test_parse_with_start_time_and_with_finish_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time == s1
    assert d["result"].finish_time == f1
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time == s1
    assert d["result"].punched_finish_time == f1
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_without_start_time_and_with_finish_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time is None
    assert d["result"].finish_time == f1
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time is None
    assert d["result"].punched_finish_time == f1
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_with_start_time_and_without_finish_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time == s1
    assert d["result"].finish_time is None
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time == s1
    assert d["result"].punched_finish_time is None
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_without_start_time_and_without_finish_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time is None
    assert d["result"].finish_time is None
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time is None
    assert d["result"].punched_finish_time is None
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_with_clear_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    cl = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "clearTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time is None
    assert d["result"].finish_time is None
    assert d["result"].punched_clear_time == cl
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time is None
    assert d["result"].punched_finish_time is None
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_with_check_time():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    ch = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "checkTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time is None
    assert d["result"].finish_time is None
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time == ch
    assert d["result"].punched_start_time is None
    assert d["result"].punched_finish_time is None
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 2
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="103", punch_time=c2, time=None, status="Additional"
    )


def test_parse_without_controls():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time == s1
    assert d["result"].finish_time == f1
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time == s1
    assert d["result"].punched_finish_time == f1
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 0
    assert d["result"].split_times == []


def test_parse_with_many_controls():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
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
    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "105", "punchTime": "2015-01-01T12:39:03Z"},
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:05Z"},
            {"controlCode": "102", "punchTime": "2015-01-01T12:39:07Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:09Z"},
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:11Z"},
            {"controlCode": "104", "punchTime": "2015-01-01T12:39:13Z"},
        ],
        "finishTime": "2015-01-01T12:39:15Z",
    }

    d = model.parse_cardreader_log(item=item)
    assert d["entryType"] == "cardRead"
    assert d["entryTime"] == e1
    assert d["controlCard"] == "123"
    assert d["result"].start_time == s1
    assert d["result"].finish_time == f1
    assert d["result"].punched_clear_time is None
    assert d["result"].punched_check_time is None
    assert d["result"].punched_start_time == s1
    assert d["result"].punched_finish_time == f1
    assert d["result"].time is None
    assert d["result"].status == ResultStatus.FINISHED
    assert len(d["result"].split_times) == 7
    assert d["result"].split_times[0] == SplitTime(
        control_code="101", punch_time=c1, time=None, status="Additional"
    )
    assert d["result"].split_times[1] == SplitTime(
        control_code="105", punch_time=c2, time=None, status="Additional"
    )
    assert d["result"].split_times[2] == SplitTime(
        control_code="101", punch_time=c3, time=None, status="Additional"
    )
    assert d["result"].split_times[3] == SplitTime(
        control_code="102", punch_time=c4, time=None, status="Additional"
    )
    assert d["result"].split_times[4] == SplitTime(
        control_code="103", punch_time=c5, time=None, status="Additional"
    )
    assert d["result"].split_times[5] == SplitTime(
        control_code="101", punch_time=c6, time=None, status="Additional"
    )
    assert d["result"].split_times[6] == SplitTime(
        control_code="104", punch_time=c7, time=None, status="Additional"
    )


def test_parse_without_entry_type_raises_exception():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    with pytest.raises(jsonschema.ValidationError):
        d = model.parse_cardreader_log(item=item)


def test_parse_without_entry_time_raises_exception():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "startTime": "2015-01-01T12:38:59Z",
        "controlCard": "123",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    with pytest.raises(jsonschema.ValidationError):
        d = model.parse_cardreader_log(item=item)


def test_parse_without_control_card_raises_exception():
    e1 = datetime(2015, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    s1 = datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
    c1 = datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
    c2 = datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
    f1 = datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)

    item = {
        "entryType": "cardRead",
        "entryTime": "2015-01-01T13:00:00Z",
        "startTime": "2015-01-01T12:38:59Z",
        "punches": [
            {"controlCode": "101", "punchTime": "2015-01-01T12:39:01Z"},
            {"controlCode": "103", "punchTime": "2015-01-01T12:39:05Z"},
        ],
        "finishTime": "2015-01-01T12:39:07Z",
    }

    with pytest.raises(jsonschema.ValidationError):
        d = model.parse_cardreader_log(item=item)

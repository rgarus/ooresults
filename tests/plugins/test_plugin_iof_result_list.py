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


from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from ooresults.plugins import iof_result_list
from ooresults.plugins.iof_result_list import ResultListStatus
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo import result_type
from ooresults.repo import start_type
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SpStatus


def test_import_result_list():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>32</ControlCode>
          <Time>720</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>818</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>1593</Time>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                start_time=s,
                finish_time=f,
                punched_start_time=s,
                punched_finish_time=f,
                si_punched_start_time=s,
                si_punched_finish_time=f,
                status=ResultStatus.OK,
                time=2001,
                split_times=[
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=501),
                        si_punch_time=s + timedelta(seconds=501),
                        time=501,
                    ),
                    result_type.SplitTime(
                        control_code="32",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=720),
                        si_punch_time=s + timedelta(seconds=720),
                        time=720,
                    ),
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=818),
                        si_punch_time=s + timedelta(seconds=818),
                        time=818,
                    ),
                    result_type.SplitTime(
                        control_code="33",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=1136),
                        si_punch_time=s + timedelta(seconds=1136),
                        time=1136,
                    ),
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=1593),
                        si_punch_time=s + timedelta(seconds=1593),
                        time=1593,
                    ),
                ],
            ),
        },
    ]


def test_import_result_list_not_competing():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <Status>NotCompeting</Status>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
            "not_competing": True,
            "result": result_type.PersonRaceResult(
                start_time=s,
                finish_time=f,
                punched_start_time=s,
                punched_finish_time=f,
                si_punched_start_time=s,
                si_punched_finish_time=f,
                status=ResultStatus.OK,
                time=2001,
            ),
        },
    ]


def test_export_result_list():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>32</ControlCode>
          <Time>720</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>818</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>1593</Time>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=None,
                    course_name=None,
                    course_length=None,
                    course_climb=None,
                    number_of_controls=None,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            club_id=1,
                            club_name="OC Kanzleramt",
                            chip="1234567",
                            gender="F",
                            year=1972,
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                start_time=s,
                                finish_time=f,
                                status=ResultStatus.OK,
                                time=2001,
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=501
                                    ),
                                    result_type.SplitTime(
                                        control_code="32", status=SpStatus.OK, time=720
                                    ),
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=818
                                    ),
                                    result_type.SplitTime(
                                        control_code="33", status=SpStatus.OK, time=1136
                                    ),
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=1593
                                    ),
                                ],
                            ),
                        ),
                        rank=1,
                        time_behind=0,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_export_result_list_not_competing():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <Status>NotCompeting</Status>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=None,
                    course_name=None,
                    course_length=None,
                    course_climb=None,
                    number_of_controls=None,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            club_id=1,
                            club_name="OC Kanzleramt",
                            chip="1234567",
                            gender="F",
                            year=1972,
                            not_competing=True,
                            result=result_type.PersonRaceResult(
                                start_time=s,
                                finish_time=f,
                                status=ResultStatus.OK,
                                time=2001,
                            ),
                        ),
                        rank=None,
                        time_behind=None,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_result_list_with_start_time_but_not_finished():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <Status>DidNotStart</Status>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DID_NOT_START,
            ),
            "start": start_type.PersonRaceStart(
                start_time=s,
            ),
        },
    ]


def test_export_result_list_with_start_time_but_not_started():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <Status>DidNotStart</Status>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=None,
                    course_name=None,
                    course_length=None,
                    course_climb=None,
                    number_of_controls=None,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            club_id=1,
                            club_name="OC Kanzleramt",
                            chip="1234567",
                            gender="F",
                            year=1972,
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                status=ResultStatus.DID_NOT_START,
                            ),
                            start=start_type.PersonRaceStart(
                                start_time=s,
                            ),
                        ),
                        rank=None,
                        time_behind=None,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_result_list_without_class_result():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == []


def test_export_result_list_without_class_result():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_result_list_classes():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:05:00Z</StartTime>
        <FinishTime>2020-02-09T10:25:21Z</FinishTime>
        <Time>1221</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>301</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>42</ControlCode>
          <Time>526</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>914</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>43</ControlCode>
          <Time>1100</Time>
        </SplitTime>
      </Result>
    </PersonResult>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Birgit</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:06:00+00:00</StartTime>
        <Status>DidNotFinish</Status>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>42</ControlCode>
          <Time>720</Time>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>41</ControlCode>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>43</ControlCode>
        </SplitTime>
      </Result>
    </PersonResult>
  </ClassResult>
  <ClassResult>
    <Class>
      <Name>Bahn B - Mittel</Name>
    </Class>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Claudia</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:00:00Z</StartTime>
        <FinishTime>2020-02-09T10:33:21Z</FinishTime>
        <Time>2001</Time>
        <Status>MissingPunch</Status>
        <SplitTime status="OK">
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>32</ControlCode>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>31</ControlCode>
        </SplitTime>
        <SplitTime status="Additional">
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s_am = datetime(2020, 2, 9, 10, 5, 0, tzinfo=timezone.utc)
    f_am = datetime(2020, 2, 9, 10, 25, 21, tzinfo=timezone.utc)
    s_bm = datetime(2020, 2, 9, 10, 6, 0, tzinfo=timezone.utc)
    s_cm = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone.utc)
    f_cm = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone.utc)

    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.OK,
                start_time=s_am,
                finish_time=f_am,
                punched_start_time=s_am,
                punched_finish_time=f_am,
                si_punched_start_time=s_am,
                si_punched_finish_time=f_am,
                time=1221,
                split_times=[
                    result_type.SplitTime(
                        control_code="41",
                        status=SpStatus.OK,
                        punch_time=s_am + timedelta(seconds=301),
                        si_punch_time=s_am + timedelta(seconds=301),
                        time=301,
                    ),
                    result_type.SplitTime(
                        control_code="42",
                        status=SpStatus.OK,
                        punch_time=s_am + timedelta(seconds=526),
                        si_punch_time=s_am + timedelta(seconds=526),
                        time=526,
                    ),
                    result_type.SplitTime(
                        control_code="41",
                        status=SpStatus.OK,
                        punch_time=s_am + timedelta(seconds=914),
                        si_punch_time=s_am + timedelta(seconds=914),
                        time=914,
                    ),
                    result_type.SplitTime(
                        control_code="43",
                        status=SpStatus.OK,
                        punch_time=s_am + timedelta(seconds=1100),
                        si_punch_time=s_am + timedelta(seconds=1100),
                        time=1100,
                    ),
                ],
            ),
        },
        {
            "first_name": "Birgit",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DID_NOT_FINISH,
                start_time=s_bm,
                punched_start_time=s_bm,
                si_punched_start_time=s_bm,
                split_times=[
                    result_type.SplitTime(
                        control_code="41",
                        status=SpStatus.OK,
                        punch_time=s_bm + timedelta(seconds=501),
                        si_punch_time=s_bm + timedelta(seconds=501),
                        time=501,
                    ),
                    result_type.SplitTime(
                        control_code="42",
                        status=SpStatus.OK,
                        punch_time=s_bm + timedelta(seconds=720),
                        si_punch_time=s_bm + timedelta(seconds=720),
                        time=720,
                    ),
                    result_type.SplitTime(control_code="41", status=SpStatus.MISSING),
                    result_type.SplitTime(control_code="43", status=SpStatus.MISSING),
                ],
            ),
        },
        {
            "first_name": "Claudia",
            "last_name": "Merkel",
            "class_": "Bahn B - Mittel",
            "club": "",
            "chip": "1234567",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.MISSING_PUNCH,
                start_time=s_cm,
                finish_time=f_cm,
                punched_start_time=s_cm,
                punched_finish_time=f_cm,
                si_punched_start_time=s_cm,
                si_punched_finish_time=f_cm,
                time=2001,
                split_times=[
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=s_cm + timedelta(seconds=501),
                        si_punch_time=s_cm + timedelta(seconds=501),
                        time=501,
                    ),
                    result_type.SplitTime(control_code="32", status=SpStatus.MISSING),
                    result_type.SplitTime(control_code="31", status=SpStatus.MISSING),
                    result_type.SplitTime(
                        control_code="33",
                        status=SpStatus.ADDITIONAL,
                        punch_time=s_cm + timedelta(seconds=1136),
                        si_punch_time=s_cm + timedelta(seconds=1136),
                        time=1136,
                    ),
                ],
            ),
        },
    ]


def test_export_result_list_classes():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <Course>
      <Name>Bahn A</Name>
      <Length>5100</Length>
      <Climb>110</Climb>
      <NumberOfControls>10</NumberOfControls>
    </Course>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:05:00+00:00</StartTime>
        <FinishTime>2020-02-09T10:25:21+00:00</FinishTime>
        <Time>1221</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>301</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>42</ControlCode>
          <Time>526</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>914</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>43</ControlCode>
          <Time>1100</Time>
        </SplitTime>
      </Result>
    </PersonResult>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Birgit</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:06:00+00:00</StartTime>
        <Status>DidNotFinish</Status>
        <SplitTime>
          <ControlCode>41</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>42</ControlCode>
          <Time>720</Time>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>41</ControlCode>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>43</ControlCode>
        </SplitTime>
      </Result>
    </PersonResult>
  </ClassResult>
  <ClassResult>
    <Class>
      <Name>Bahn B - Mittel</Name>
    </Class>
    <Course>
      <Name>Bahn B</Name>
      <Length>2800</Length>
    </Course>
    <PersonResult>
      <Person>
        <Name>
          <Family>Merkel</Family>
          <Given>Claudia</Given>
        </Name>
      </Person>
      <Result>
        <StartTime>2020-02-09T10:00:00+00:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+00:00</FinishTime>
        <Time>2001</Time>
        <Status>MissingPunch</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>32</ControlCode>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>31</ControlCode>
        </SplitTime>
        <SplitTime status="Additional">
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=1,
                    course_name="Bahn A",
                    course_length=5100,
                    course_climb=110,
                    number_of_controls=10,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                status=ResultStatus.OK,
                                start_time=datetime(
                                    2020, 2, 9, 10, 5, 0, tzinfo=timezone.utc
                                ),
                                finish_time=datetime(
                                    2020, 2, 9, 10, 25, 21, tzinfo=timezone.utc
                                ),
                                time=1221,
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="41", status=SpStatus.OK, time=301
                                    ),
                                    result_type.SplitTime(
                                        control_code="42", status=SpStatus.OK, time=526
                                    ),
                                    result_type.SplitTime(
                                        control_code="41", status=SpStatus.OK, time=914
                                    ),
                                    result_type.SplitTime(
                                        control_code="43", status=SpStatus.OK, time=1100
                                    ),
                                ],
                            ),
                        ),
                        rank=1,
                        time_behind=0,
                    ),
                    RankedEntryType(
                        entry=EntryType(
                            id=2,
                            event_id=1,
                            competitor_id=2,
                            first_name="Birgit",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                status=ResultStatus.DID_NOT_FINISH,
                                start_time=datetime(
                                    2020, 2, 9, 10, 6, 0, tzinfo=timezone.utc
                                ),
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="41", status=SpStatus.OK, time=501
                                    ),
                                    result_type.SplitTime(
                                        control_code="42", status=SpStatus.OK, time=720
                                    ),
                                    result_type.SplitTime(
                                        control_code="41", status=SpStatus.MISSING
                                    ),
                                    result_type.SplitTime(
                                        control_code="43", status=SpStatus.MISSING
                                    ),
                                ],
                            ),
                        ),
                        rank=None,
                        time_behind=None,
                    ),
                ],
            ),
            (
                ClassInfoType(
                    id=2,
                    name="Bahn B - Mittel",
                    short_name=None,
                    course_id=2,
                    course_name="Bahn B",
                    course_length=2800,
                    course_climb=None,
                    number_of_controls=0,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=3,
                            event_id=1,
                            competitor_id=3,
                            first_name="Claudia",
                            last_name="Merkel",
                            class_id=2,
                            class_name="Bahn B - Mittel",
                            not_competing=False,
                            chip="1234567",
                            result=result_type.PersonRaceResult(
                                status=ResultStatus.MISSING_PUNCH,
                                start_time=datetime(
                                    2020, 2, 9, 10, 0, 0, tzinfo=timezone.utc
                                ),
                                finish_time=datetime(
                                    2020, 2, 9, 10, 33, 21, tzinfo=timezone.utc
                                ),
                                time=2001,
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="31",
                                        status=SpStatus.OK,
                                        time=501,
                                    ),
                                    result_type.SplitTime(
                                        control_code="32",
                                        status=SpStatus.MISSING,
                                    ),
                                    result_type.SplitTime(
                                        control_code="31",
                                        status=SpStatus.MISSING,
                                    ),
                                    result_type.SplitTime(
                                        control_code="33",
                                        status=SpStatus.ADDITIONAL,
                                        time=1136,
                                    ),
                                ],
                            ),
                        ),
                        rank=None,
                        time_behind=None,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_result_list_with_unknown_punch_times():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>32</ControlCode>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <SplitTime>
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    event, results, status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert status is None
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                start_time=s,
                finish_time=f,
                punched_start_time=s,
                punched_finish_time=f,
                si_punched_start_time=s,
                si_punched_finish_time=f,
                status=ResultStatus.OK,
                time=2001,
                split_times=[
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=501),
                        si_punch_time=s + timedelta(seconds=501),
                        time=501,
                    ),
                    result_type.SplitTime(
                        control_code="32",
                        status=SpStatus.OK,
                        punch_time=result_type.SplitTime.NO_TIME,
                        time=None,
                    ),
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=result_type.SplitTime.NO_TIME,
                        time=None,
                    ),
                    result_type.SplitTime(
                        control_code="33",
                        status=SpStatus.OK,
                        punch_time=s + timedelta(seconds=1136),
                        si_punch_time=s + timedelta(seconds=1136),
                        time=1136,
                    ),
                    result_type.SplitTime(
                        control_code="31",
                        status=SpStatus.OK,
                        punch_time=result_type.SplitTime.NO_TIME,
                        time=None,
                    ),
                ],
            ),
        },
    ]


def test_export_result_list_with_unknown_punch_times():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>32</ControlCode>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <SplitTime>
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=None,
                    course_name=None,
                    course_length=None,
                    course_climb=None,
                    number_of_controls=None,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            club_id=1,
                            club_name="OC Kanzleramt",
                            chip="1234567",
                            gender="F",
                            year=1972,
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                start_time=s,
                                finish_time=f,
                                status=ResultStatus.OK,
                                time=2001,
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=501
                                    ),
                                    result_type.SplitTime(
                                        control_code="32", status=SpStatus.OK, time=None
                                    ),
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=None
                                    ),
                                    result_type.SplitTime(
                                        control_code="33", status=SpStatus.OK, time=1136
                                    ),
                                    result_type.SplitTime(
                                        control_code="31", status=SpStatus.OK, time=None
                                    ),
                                ],
                            ),
                        ),
                        rank=1,
                        time_behind=0,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_export_result_list_with_edited_punch_times():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <ClassResult>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
    <PersonResult>
      <Person sex="F">
        <Name>
          <Family>Merkel</Family>
          <Given>Angela</Given>
        </Name>
        <BirthDate>1972-01-01</BirthDate>
      </Person>
      <Organisation>
        <Name>OC Kanzleramt</Name>
      </Organisation>
      <Result>
        <StartTime>2020-02-09T10:00:00+01:00</StartTime>
        <FinishTime>2020-02-09T10:33:21+01:00</FinishTime>
        <Time>2001</Time>
        <TimeBehind>0</TimeBehind>
        <Position>1</Position>
        <Status>OK</Status>
        <SplitTime>
          <ControlCode>31</ControlCode>
          <Time>501</Time>
        </SplitTime>
        <SplitTime status="Missing">
          <ControlCode>32</ControlCode>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <SplitTime status="Additional">
          <ControlCode>33</ControlCode>
          <Time>1136</Time>
        </SplitTime>
        <SplitTime>
          <ControlCode>31</ControlCode>
        </SplitTime>
        <ControlCard punchingSystem="SI">1234567</ControlCard>
      </Result>
    </PersonResult>
  </ClassResult>
</ResultList>
"""
    s = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    document = iof_result_list.create_result_list(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            (
                ClassInfoType(
                    id=1,
                    name="Bahn A - Lang",
                    short_name=None,
                    course_id=None,
                    course_name=None,
                    course_length=None,
                    course_climb=None,
                    number_of_controls=None,
                    params=ClassParams(),
                ),
                [
                    RankedEntryType(
                        entry=EntryType(
                            id=1,
                            event_id=1,
                            competitor_id=1,
                            first_name="Angela",
                            last_name="Merkel",
                            class_id=1,
                            class_name="Bahn A - Lang",
                            club_id=1,
                            club_name="OC Kanzleramt",
                            chip="1234567",
                            gender="F",
                            year=1972,
                            not_competing=False,
                            result=result_type.PersonRaceResult(
                                start_time=s,
                                finish_time=f,
                                status=ResultStatus.OK,
                                time=2001,
                                split_times=[
                                    result_type.SplitTime(
                                        control_code="31",
                                        status=SpStatus.OK,
                                        time=501,
                                    ),
                                    result_type.SplitTime(
                                        control_code="32",
                                        status=SpStatus.MISSING,
                                        time=None,
                                    ),
                                    result_type.SplitTime(
                                        control_code="34",
                                        status=None,
                                        time=None,
                                    ),
                                    result_type.SplitTime(
                                        control_code="31",
                                        status=SpStatus.OK,
                                        time=None,
                                    ),
                                    result_type.SplitTime(
                                        control_code="33",
                                        status=SpStatus.ADDITIONAL,
                                        time=1136,
                                    ),
                                    result_type.SplitTime(
                                        control_code="34",
                                        status=None,
                                        time=None,
                                    ),
                                    result_type.SplitTime(
                                        control_code="31",
                                        status=SpStatus.OK,
                                        time=None,
                                    ),
                                ],
                            ),
                        ),
                        rank=1,
                        time_behind=0,
                    ),
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")


@pytest.mark.parametrize(
    "status, status_xml",
    [
        (ResultListStatus.COMPLETE, 'status="Complete"'),
        (ResultListStatus.DELTA, 'status="Delta"'),
        (ResultListStatus.SNAPSHOT, 'status="Snapshot"'),
    ],
)
def test_import_result_list_with_status_attribute(
    status: ResultListStatus, status_xml: str
):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" {attr}>
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    content = content.replace("{attr}", status_xml)

    event, results, _status = iof_result_list.parse_result_list(
        bytes(content, encoding="utf-8")
    )
    assert _status == status
    assert event == {
        "name": "1. O-Cup 2020",
        "date": date(year=2020, month=2, day=9),
    }
    assert results == []


@pytest.mark.parametrize(
    "status, status_xml",
    [
        (ResultListStatus.COMPLETE, 'status="Complete"'),
        (ResultListStatus.DELTA, 'status="Delta"'),
        (ResultListStatus.SNAPSHOT, 'status="Snapshot"'),
    ],
)
def test_export_result_list_with_status_comp(status: ResultListStatus, status_xml: str):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)" {attr}>
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    content = content.replace("{attr}", status_xml)

    document = iof_result_list.create_result_list(
        event=EventType(
            id=1,
            name="1. O-Cup 2020",
            date=date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        class_results=[],
        status=status,
    )
    assert document == bytes(content, encoding="utf-8")

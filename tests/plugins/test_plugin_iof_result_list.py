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


import datetime
from datetime import timezone
from datetime import timedelta

from ooresults.plugins import iof_result_list
from ooresults.repo import result_type
from ooresults.repo.result_type import ResultStatus


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
    event, results = iof_result_list.parse_result_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
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
                start_time=datetime.datetime(
                    2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                ),
                finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                ),
                punched_start_time=datetime.datetime(
                    2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                ),
                punched_finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                ),
                status=ResultStatus.OK,
                time=2001,
                split_times=[
                    result_type.SplitTime(control_code="31", status="OK", time=501),
                    result_type.SplitTime(control_code="32", status="OK", time=720),
                    result_type.SplitTime(control_code="31", status="OK", time=818),
                    result_type.SplitTime(control_code="33", status="OK", time=1136),
                    result_type.SplitTime(control_code="31", status="OK", time=1593),
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
    event, results = iof_result_list.parse_result_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
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
                start_time=datetime.datetime(
                    2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                ),
                finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                ),
                punched_start_time=datetime.datetime(
                    2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                ),
                punched_finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                ),
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
    document = iof_result_list.create_result_list(
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [
            (
                {
                    "name": "Bahn A - Lang",
                    "course_length": None,
                    "course_climb": None,
                    "number_of_controls": None,
                },
                [
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
                            start_time=datetime.datetime(
                                2020,
                                2,
                                9,
                                10,
                                0,
                                0,
                                tzinfo=timezone(timedelta(hours=1)),
                            ),
                            finish_time=datetime.datetime(
                                2020,
                                2,
                                9,
                                10,
                                33,
                                21,
                                tzinfo=timezone(timedelta(hours=1)),
                            ),
                            status=ResultStatus.OK,
                            time=2001,
                            split_times=[
                                result_type.SplitTime(
                                    control_code="31", status="OK", time=501
                                ),
                                result_type.SplitTime(
                                    control_code="32", status="OK", time=720
                                ),
                                result_type.SplitTime(
                                    control_code="31", status="OK", time=818
                                ),
                                result_type.SplitTime(
                                    control_code="33", status="OK", time=1136
                                ),
                                result_type.SplitTime(
                                    control_code="31", status="OK", time=1593
                                ),
                            ],
                        ),
                        "time_behind": 0,
                        "rank": 1,
                    },
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
    document = iof_result_list.create_result_list(
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [
            (
                {
                    "name": "Bahn A - Lang",
                    "course_length": None,
                    "course_climb": None,
                    "number_of_controls": None,
                },
                [
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
                            start_time=datetime.datetime(
                                2020,
                                2,
                                9,
                                10,
                                0,
                                0,
                                tzinfo=timezone(timedelta(hours=1)),
                            ),
                            finish_time=datetime.datetime(
                                2020,
                                2,
                                9,
                                10,
                                33,
                                21,
                                tzinfo=timezone(timedelta(hours=1)),
                            ),
                            status=ResultStatus.OK,
                            time=2001,
                        ),
                        "rank": None,
                    },
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
    event, results = iof_result_list.parse_result_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
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
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
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
    event, results = iof_result_list.parse_result_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
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
                start_time=datetime.datetime(2020, 2, 9, 10, 5, 0, tzinfo=timezone.utc),
                finish_time=datetime.datetime(
                    2020, 2, 9, 10, 25, 21, tzinfo=timezone.utc
                ),
                punched_start_time=datetime.datetime(
                    2020, 2, 9, 10, 5, 0, tzinfo=timezone.utc
                ),
                punched_finish_time=datetime.datetime(
                    2020, 2, 9, 10, 25, 21, tzinfo=timezone.utc
                ),
                time=1221,
                split_times=[
                    result_type.SplitTime(control_code="41", status="OK", time=301),
                    result_type.SplitTime(control_code="42", status="OK", time=526),
                    result_type.SplitTime(control_code="41", status="OK", time=914),
                    result_type.SplitTime(control_code="43", status="OK", time=1100),
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
                start_time=datetime.datetime(2020, 2, 9, 10, 6, 0, tzinfo=timezone.utc),
                punched_start_time=datetime.datetime(
                    2020, 2, 9, 10, 6, 0, tzinfo=timezone.utc
                ),
                split_times=[
                    result_type.SplitTime(control_code="41", status="OK", time=501),
                    result_type.SplitTime(control_code="42", status="OK", time=720),
                    result_type.SplitTime(control_code="41", status="Missing"),
                    result_type.SplitTime(control_code="43", status="Missing"),
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
                start_time=datetime.datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone.utc),
                finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone.utc
                ),
                punched_start_time=datetime.datetime(
                    2020, 2, 9, 10, 0, 0, tzinfo=timezone.utc
                ),
                punched_finish_time=datetime.datetime(
                    2020, 2, 9, 10, 33, 21, tzinfo=timezone.utc
                ),
                time=2001,
                split_times=[
                    result_type.SplitTime(control_code="31", status="OK", time=501),
                    result_type.SplitTime(control_code="32", status="Missing"),
                    result_type.SplitTime(control_code="31", status="Missing"),
                    result_type.SplitTime(
                        control_code="33", status="Additional", time=1136
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
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [
            (
                {
                    "name": "Bahn A - Lang",
                    "course_length": 5100.0,
                    "course_climb": 110.0,
                    "number_of_controls": 10,
                },
                [
                    {
                        "first_name": "Angela",
                        "last_name": "Merkel",
                        "class_": "Bahn A - Lang",
                        "not_competing": False,
                        "result": result_type.PersonRaceResult(
                            status=ResultStatus.OK,
                            start_time=datetime.datetime(
                                2020, 2, 9, 10, 5, 0, tzinfo=timezone.utc
                            ),
                            finish_time=datetime.datetime(
                                2020, 2, 9, 10, 25, 21, tzinfo=timezone.utc
                            ),
                            time=1221,
                            split_times=[
                                result_type.SplitTime(
                                    control_code="41", status="OK", time=301
                                ),
                                result_type.SplitTime(
                                    control_code="42", status="OK", time=526
                                ),
                                result_type.SplitTime(
                                    control_code="41", status="OK", time=914
                                ),
                                result_type.SplitTime(
                                    control_code="43", status="OK", time=1100
                                ),
                            ],
                        ),
                        "time_behind": 0,
                        "rank": 1,
                    },
                    {
                        "first_name": "Birgit",
                        "last_name": "Merkel",
                        "class_": "Bahn A - Lang",
                        "not_competing": False,
                        "result": result_type.PersonRaceResult(
                            status=ResultStatus.DID_NOT_FINISH,
                            start_time=datetime.datetime(
                                2020, 2, 9, 10, 6, 0, tzinfo=timezone.utc
                            ),
                            split_times=[
                                result_type.SplitTime(
                                    control_code="41", status="OK", time=501
                                ),
                                result_type.SplitTime(
                                    control_code="42", status="OK", time=720
                                ),
                                result_type.SplitTime(
                                    control_code="41", status="Missing"
                                ),
                                result_type.SplitTime(
                                    control_code="43", status="Missing"
                                ),
                            ],
                        ),
                        "rank": None,
                    },
                ],
            ),
            (
                {
                    "name": "Bahn B - Mittel",
                    "course_length": 2800.0,
                    "course_climb": None,
                    "number_of_controls": 0,
                },
                [
                    {
                        "first_name": "Claudia",
                        "last_name": "Merkel",
                        "class_": "Bahn B - Mittel",
                        "chip": "1234567",
                        "not_competing": False,
                        "result": result_type.PersonRaceResult(
                            status=ResultStatus.MISSING_PUNCH,
                            start_time=datetime.datetime(
                                2020, 2, 9, 10, 0, 0, tzinfo=timezone.utc
                            ),
                            finish_time=datetime.datetime(
                                2020, 2, 9, 10, 33, 21, tzinfo=timezone.utc
                            ),
                            time=2001,
                            split_times=[
                                result_type.SplitTime(
                                    control_code="31", status="OK", time=501
                                ),
                                result_type.SplitTime(
                                    control_code="32", status="Missing"
                                ),
                                result_type.SplitTime(
                                    control_code="31", status="Missing"
                                ),
                                result_type.SplitTime(
                                    control_code="33", status="Additional", time=1136
                                ),
                            ],
                        ),
                        "rank": None,
                    },
                ],
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")

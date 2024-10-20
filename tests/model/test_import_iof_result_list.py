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
import tempfile
from datetime import timedelta
from datetime import timezone

import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.model import model
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.class_params import ClassParams
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.competitor_type import CompetitorType
from ooresults.repo.start_type import PersonRaceStart


@pytest.fixture
def db() -> SqliteRepo:
    with tempfile.NamedTemporaryFile() as db_file:
        model.db = SqliteRepo(db=db_file.name)
        yield model.db


@pytest.fixture
def event_id(db: SqliteRepo) -> int:
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key="local",
        publish=False,
        series=None,
        fields=[],
    )


@pytest.fixture
def class_id(db: SqliteRepo, event_id: int) -> int:
    return db.add_class(
        event_id=event_id,
        name="Elite",
        short_name="E",
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def entry_id(db: SqliteRepo, event_id: int, class_id: int) -> int:
    return db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Robert",
        last_name="Lewandowski",
        gender="",
        year=None,
        class_id=class_id,
        club_id=None,
        not_competing=False,
        chip="9999999",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )


def test_import_iof_result_list_snapshot(
    event_id: int,
    entry_id: int,
):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" status="Snapshot">
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
    s = datetime.datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime.datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    model.import_iof_result_list(
        event_key="local",
        content=content.encode(),
    )

    competitors = model.get_competitors()
    assert competitors == [
        CompetitorType(
            id=competitors[0].id,
            first_name="Robert",
            last_name="Lewandowski",
            club_id=None,
            club_name=None,
            gender="",
            year=None,
            chip="9999999",
        ),
        CompetitorType(
            id=competitors[1].id,
            first_name="Angela",
            last_name="Merkel",
            club_id=None,
            club_name=None,
            gender="F",
            year=1972,
            chip="1234567",
        ),
    ]

    classes = model.get_classes(event_id=event_id)
    assert classes == [
        ClassInfoType(
            id=classes[0].id,
            name="Bahn A - Lang",
            short_name=None,
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
    ]

    entries = model.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=competitors[1].id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1972,
            class_id=classes[0].id,
            class_name="Bahn A - Lang",
            not_competing=True,
            chip="1234567",
            fields={},
            result=PersonRaceResult(
                start_time=s,
                finish_time=f,
                punched_start_time=s,
                punched_finish_time=f,
                si_punched_start_time=s,
                si_punched_finish_time=f,
                status=ResultStatus.OK,
                time=2001,
            ),
            start=PersonRaceStart(),
            club_id=None,
            club_name=None,
        ),
    ]


def test_import_iof_result_list_delta(
    event_id: int,
    entry_id: int,
):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" status="Delta">
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
    s = datetime.datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    f = datetime.datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))

    model.import_iof_result_list(
        event_key="local",
        content=content.encode(),
    )

    competitors = model.get_competitors()
    assert competitors == [
        CompetitorType(
            id=competitors[0].id,
            first_name="Robert",
            last_name="Lewandowski",
            club_id=None,
            club_name=None,
            gender="",
            year=None,
            chip="9999999",
        ),
        CompetitorType(
            id=competitors[1].id,
            first_name="Angela",
            last_name="Merkel",
            club_id=None,
            club_name=None,
            gender="F",
            year=1972,
            chip="1234567",
        ),
    ]

    classes = model.get_classes(event_id=event_id)
    assert classes == [
        ClassInfoType(
            id=classes[0].id,
            name="Bahn A - Lang",
            short_name=None,
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
        ClassInfoType(
            id=classes[1].id,
            name="Elite",
            short_name="E",
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
    ]

    entries = model.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=competitors[0].id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=classes[1].id,
            class_name="Elite",
            not_competing=False,
            chip="9999999",
            fields={},
            result=PersonRaceResult(),
            start=PersonRaceStart(),
            club_id=None,
            club_name=None,
        ),
        EntryType(
            id=entries[1].id,
            event_id=event_id,
            competitor_id=competitors[1].id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1972,
            class_id=classes[0].id,
            class_name="Bahn A - Lang",
            not_competing=True,
            chip="1234567",
            fields={},
            result=PersonRaceResult(
                start_time=s,
                finish_time=f,
                punched_start_time=s,
                punched_finish_time=f,
                si_punched_start_time=s,
                si_punched_finish_time=f,
                status=ResultStatus.OK,
                time=2001,
            ),
            start=PersonRaceStart(),
            club_id=None,
            club_name=None,
        ),
    ]

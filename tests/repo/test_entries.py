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
from datetime import timedelta
from datetime import timezone

import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo import result_type
from ooresults.repo.result_type import ResultStatus
from ooresults.repo import start_type


S1 = datetime.datetime(2021, 8, 19, 18, 43, 33, tzinfo=timezone(timedelta(hours=2)))
S2 = datetime.datetime(2021, 8, 18, 17, 55, 00, tzinfo=timezone(timedelta(hours=2)))
S3 = datetime.datetime(2021, 8, 17, 10, 12, 14, tzinfo=timezone(timedelta(hours=2)))


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def event_1_id(db):
    return db.add_event(
        name="event 1",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
    )


@pytest.fixture
def event_2_id(db):
    return db.add_event(
        name="event 2",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
    )


@pytest.fixture
def class_1_id(db, event_2_id):
    return db.add_class(
        event_id=event_2_id,
        name="Class 1",
        short_name=None,
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_2_id(db, event_2_id):
    return db.add_class(
        event_id=event_2_id,
        name="Class 2",
        short_name=None,
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def club_id(db):
    return db.add_club(
        name="OL Bundestag",
    )


@pytest.fixture
def competitor_1_id(db, club_id):
    return db.add_competitor(
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        gender="",
        year=None,
        chip="1234567",
    )


@pytest.fixture
def competitor_2_id(db):
    return db.add_competitor(
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        gender="",
        year=None,
        chip="",
    )


@pytest.fixture
def entry_1_id(db, event_1_id, class_1_id, club_id):
    return db.add_entry(
        event_id=event_1_id,
        competitor_id=None,
        first_name="Robert",
        last_name="Lewandowski",
        gender="",
        year=None,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="9999999",
        fields={0: "ab", 1: "cd"},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )


@pytest.fixture
def entry_2_id(db, event_2_id, class_2_id, club_id):
    return db.add_entry(
        event_id=event_2_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        club_id=club_id,
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        status=ResultStatus.DID_NOT_START,
        start_time=S1,
    )


@pytest.fixture
def entry_3_id(db, event_2_id, class_2_id):
    return db.add_entry(
        event_id=event_2_id,
        competitor_id=None,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )


def test_get_entries(
    db, event_2_id, entry_1_id, entry_2_id, entry_3_id, club_id, class_2_id
):
    data = db.get_entries(event_id=event_2_id)
    print(data[0])
    assert len(data) == 2

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == ""
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.INACTIVE
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_2_id
    assert data[0]["class_"] == "Class 2"

    assert data[1]["id"] == entry_2_id
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == "F"
    assert data[1]["year"] == 1957
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "9999999"
    assert data[1]["fields"] == {0: "x"}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_2_id
    assert data[1]["class_"] == "Class 2"


def test_get_first_added_entry(
    db, event_2_id, club_id, class_2_id, entry_1_id, entry_2_id, entry_3_id
):
    competitors = list(db.get_competitors())
    competitor = [
        c for c in competitors if c.first_name == "Angela" and c.last_name == "Merkel"
    ][0]

    assert competitor["first_name"] == "Angela"
    assert competitor["last_name"] == "Merkel"
    assert competitor["gender"] == "F"
    assert competitor["year"] == 1957
    assert competitor["chip"] == "9999999"
    assert competitor["club_name"] == "OL Bundestag"
    assert competitor["club_id"] == club_id

    data = list(db.get_entry(id=entry_2_id))
    assert len(data) == 1

    assert data[0]["id"] == entry_2_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["competitor_id"] == competitor.id
    assert data[0]["first_name"] == "Angela"
    assert data[0]["last_name"] == "Merkel"
    assert data[0]["gender"] == "F"
    assert data[0]["year"] == 1957
    assert data[0]["not_competing"] is True
    assert data[0]["chip"] == "9999999"
    assert data[0]["fields"] == {0: "x"}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[0]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[0]["club"] == "OL Bundestag"
    assert data[0]["club_id"] == club_id
    assert data[0]["class_"] == "Class 2"
    assert data[0]["class_id"] == class_2_id


def test_get_last_added_entry(
    db, event_2_id, club_id, class_2_id, entry_1_id, entry_2_id, entry_3_id
):
    competitors = list(db.get_competitors())
    competitor = [
        c for c in competitors if c.first_name == "Jogi" and c.last_name == "Löw"
    ][0]

    assert competitor["first_name"] == "Jogi"
    assert competitor["last_name"] == "Löw"
    assert competitor["gender"] == "M"
    assert competitor["year"] is None
    assert competitor["chip"] == ""
    assert competitor["club_name"] is None
    assert competitor["club_id"] is None

    data = list(db.get_entry(id=entry_3_id))
    assert len(data) == 1

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["competitor_id"] == competitor.id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == ""
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.INACTIVE
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club"] is None
    assert data[0]["club_id"] is None
    assert data[0]["class_"] == "Class 2"
    assert data[0]["class_id"] == class_2_id


def test_update_first_added_entry(
    db, event_2_id, class_1_id, class_2_id, entry_2_id, entry_3_id
):
    db.update_entry(
        id=entry_2_id,
        first_name="angela",
        last_name="merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        club_id=None,
        not_competing=False,
        chip="7788",
        fields={},
        status=ResultStatus.DISQUALIFIED,
        start_time=S2,
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] is None
    assert data[0]["chip"] == ""
    assert data[0]["not_competing"] is False
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.INACTIVE
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_2_id
    assert data[0]["class_"] == "Class 2"

    assert data[1]["id"] == entry_2_id
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "angela"
    assert data[1]["last_name"] == "merkel"
    assert data[1]["gender"] == ""
    assert data[1]["year"] is None
    assert data[1]["not_competing"] is False
    assert data[1]["chip"] == "7788"
    assert data[1]["fields"] == {}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DISQUALIFIED
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S2)
    assert data[1]["club_id"] is None
    assert data[1]["club"] is None
    assert data[1]["class_id"] == class_1_id
    assert data[1]["class_"] == "Class 1"


def test_update_result_first_added_entry(
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    db.update_entry_result(
        id=entry_2_id,
        chip="7788",
        start_time=S2,
        result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == ""
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.INACTIVE
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_2_id
    assert data[0]["class_"] == "Class 2"

    assert data[1]["id"] == entry_2_id
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == "F"
    assert data[1]["year"] == 1957
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "7788"
    assert data[1]["fields"] == {0: "x"}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DISQUALIFIED
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S2)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_2_id
    assert data[1]["class_"] == "Class 2"


def test_update_last_added_entry(
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    db.update_entry(
        id=entry_3_id,
        first_name="jogi",
        last_name="Loew",
        gender="M",
        year=1960,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4455",
        fields={},
        status=ResultStatus.DID_NOT_START,
        start_time=S3,
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "jogi"
    assert data[0]["last_name"] == "Loew"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1960
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "4455"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[0]["start"] == start_type.PersonRaceStart(start_time=S3)
    assert data[0]["club_id"] == club_id
    assert data[0]["club"] == "OL Bundestag"
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"

    assert data[1]["id"] == entry_2_id
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == "F"
    assert data[1]["year"] == 1957
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "9999999"
    assert data[1]["fields"] == {0: "x"}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_2_id
    assert data[1]["class_"] == "Class 2"


def test_update_result_last_added_entry(
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    db.update_entry_result(
        id=entry_3_id,
        chip="4455",
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start_time=S3,
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] == entry_3_id
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "4455"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[0]["start"] == start_type.PersonRaceStart(start_time=S3)
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_2_id
    assert data[0]["class_"] == "Class 2"

    assert data[1]["id"] == entry_2_id
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == "F"
    assert data[1]["year"] == 1957
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "9999999"
    assert data[1]["fields"] == {0: "x"}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_2_id
    assert data[1]["class_"] == "Class 2"


def test_add_existing_competitor_but_do_not_update_competitors_chip_and_club_if_alread_defined(
    db, event_1_id, class_1_id, competitor_1_id, club_id
):
    db.add_entry(
        event_id=event_1_id,
        competitor_id=competitor_1_id,
        first_name="Angela",
        last_name="Merkel",
        gender="W",
        year=None,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="999",
        fields={},
        status=result_type.ResultStatus.INACTIVE,
        start_time=None,
    )
    data = list(db.get_entries(event_id=event_1_id))
    assert len(data) == 1

    assert data[0]["id"] is not None
    assert data[0]["event_id"] == event_1_id
    assert data[0]["competitor_id"] == competitor_1_id
    assert data[0]["first_name"] == "Angela"
    assert data[0]["last_name"] == "Merkel"
    assert data[0]["gender"] == "W"
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "999"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult()
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] == club_id
    assert data[0]["club"] == "OL Bundestag"
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"
    assert data[0]["result"] == result_type.PersonRaceResult()
    assert data[0]["start"] == start_type.PersonRaceStart()

    data = list(db.get_competitor(id=competitor_1_id))
    assert len(data) == 1

    assert data[0]["id"] == competitor_1_id
    assert data[0]["first_name"] == "Angela"
    assert data[0]["last_name"] == "Merkel"
    assert data[0]["gender"] == "W"
    assert data[0]["year"] is None
    assert data[0]["chip"] == "1234567"
    assert data[0]["club_id"] == club_id


def test_add_existing_competitor_and_update_competitors_chip_and_club_if_undefined(
    db, event_1_id, class_1_id, competitor_2_id, club_id
):
    db.add_entry(
        event_id=event_1_id,
        competitor_id=competitor_2_id,
        first_name="Yogi",
        last_name="Löw",
        gender="M",
        year=1975,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="999",
        fields={},
        status=result_type.ResultStatus.INACTIVE,
        start_time=None,
    )
    data = list(db.get_entries(event_id=event_1_id))
    assert len(data) == 1

    assert data[0]["id"] is not None
    assert data[0]["event_id"] == event_1_id
    assert data[0]["competitor_id"] == competitor_2_id
    assert data[0]["first_name"] == "Yogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1975
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "999"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult()
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] == club_id
    assert data[0]["club"] == "OL Bundestag"
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"
    assert data[0]["result"] == result_type.PersonRaceResult()
    assert data[0]["start"] == start_type.PersonRaceStart()

    data = list(db.get_competitor(id=competitor_2_id))
    assert len(data) == 1

    assert data[0]["id"] == competitor_2_id
    assert data[0]["first_name"] == "Yogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1975
    assert data[0]["chip"] == "999"
    assert data[0]["club_id"] == club_id


def test_add_entry_result(db, event_2_id, class_2_id, club_id, entry_2_id):
    entry_id_1_result = db.add_entry_result(
        event_id=event_2_id,
        chip="4455",
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start_time=S3,
    )
    entry_id_2_result = db.add_entry_result(
        event_id=event_2_id,
        chip="2289",
        result=result_type.PersonRaceResult(status=ResultStatus.MISSING_PUNCH),
        start_time=S2,
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 3

    assert data[0]["id"] == entry_id_2_result
    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] is None
    assert data[0]["last_name"] is None
    assert data[0]["gender"] is None
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "2289"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH
    )
    assert data[0]["start"] == start_type.PersonRaceStart(start_time=S2)
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] is None
    assert data[0]["class_"] is None

    assert data[1]["id"] == entry_id_1_result
    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] is None
    assert data[1]["last_name"] is None
    assert data[1]["gender"] is None
    assert data[1]["year"] is None
    assert data[1]["not_competing"] is False
    assert data[1]["chip"] == "4455"
    assert data[1]["fields"] == {}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S3)
    assert data[1]["club_id"] is None
    assert data[1]["club"] is None
    assert data[1]["class_id"] is None
    assert data[1]["class_"] is None

    assert data[2]["id"] == entry_2_id
    assert data[2]["event_id"] == event_2_id
    assert data[2]["first_name"] == "Angela"
    assert data[2]["last_name"] == "Merkel"
    assert data[2]["gender"] == "F"
    assert data[2]["year"] == 1957
    assert data[2]["not_competing"] is True
    assert data[2]["chip"] == "9999999"
    assert data[2]["fields"] == {0: "x"}
    assert data[2]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.DID_NOT_START
    )
    assert data[2]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[2]["club_id"] == club_id
    assert data[2]["club"] == "OL Bundestag"
    assert data[2]["class_id"] == class_2_id
    assert data[2]["class_"] == "Class 2"


def test_import_entries_empty_db(db, event_2_id):
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "OL Bundestag",
                "not_competing": True,
                "chip": "4455",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2361
                ),
                "start": start_type.PersonRaceStart(start_time=S1),
            },
            {
                "first_name": "Jogi",
                "last_name": "Löw",
                "gender": "M",
                "year": 1960,
                "class_": "Class 2",
                "club": "",
                "chip": "1234",
                "fields": {},
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH, time=2233
                ),
            },
        ],
    )
    classes = list(db.get_classes(event_id=event_2_id))
    assert len(classes) == 2
    assert classes[0].id != classes[1].id

    assert classes[0].name == "Class 1"
    assert classes[0].short_name is None
    assert classes[0].course_id is None
    assert classes[0].course is None
    assert classes[0].course_length is None
    assert classes[0].course_climb is None
    assert classes[0].number_of_controls is None
    assert classes[0].params == ClassParams()

    assert classes[1].name == "Class 2"
    assert classes[1].short_name is None
    assert classes[1].course_id is None
    assert classes[1].course is None
    assert classes[1].course_length is None
    assert classes[1].course_climb is None
    assert classes[1].number_of_controls is None
    assert classes[1].params == ClassParams()

    clubs = list(db.get_clubs())
    assert len(clubs) == 1

    assert clubs[0].name == "OL Bundestag"

    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year == 1960
    assert c[0].chip == "1234"

    assert c[1].first_name == "Angela"
    assert c[1].last_name == "Merkel"
    assert c[1].club_id == clubs[0].id
    assert c[1].club_name == clubs[0].name
    assert c[1].gender == ""
    assert c[1].year is None
    assert c[1].chip == "4455"

    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] != data[1]["id"]

    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1960
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "1234"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH, time=2233
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == classes[1].id
    assert data[0]["class_"] == classes[1].name

    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == ""
    assert data[1]["year"] is None
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "4455"
    assert data[1]["fields"] == {}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.OK, time=2361
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[1]["club_id"] == clubs[0].id
    assert data[1]["club"] == clubs[0].name
    assert data[1]["class_id"] == classes[0].id
    assert data[1]["class_"] == classes[0].name


def test_import_entries(db, event_2_id, class_1_id, club_id):
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "OL Bundestag",
                "chip": "4455",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2361
                ),
                "start": start_type.PersonRaceStart(start_time=S1),
            },
            {
                "first_name": "Jogi",
                "last_name": "Löw",
                "gender": "M",
                "year": 1960,
                "class_": "Class 1",
                "club": "",
                "chip": "1234",
                "fields": {},
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH, time=2233
                ),
            },
        ],
    )
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year == 1960
    assert c[0].chip == "1234"

    assert c[1].first_name == "Angela"
    assert c[1].last_name == "Merkel"
    assert c[1].club_id == club_id
    assert c[1].club_name == "OL Bundestag"
    assert c[1].gender == ""
    assert c[1].year is None
    assert c[1].chip == "4455"

    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] != data[1]["id"]

    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1960
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "1234"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH, time=2233
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"

    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == ""
    assert data[1]["year"] is None
    assert data[1]["not_competing"] is False
    assert data[1]["chip"] == "4455"
    assert data[1]["fields"] == {}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.OK, time=2361
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S1)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_1_id
    assert data[1]["class_"] == "Class 1"


def test_import_entries_already_exist(
    db, event_2_id, class_1_id, club_id, entry_2_id, entry_3_id
):
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "OL Bundestag",
                "chip": "4455",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2361
                ),
                "start": start_type.PersonRaceStart(start_time=S3),
            },
            {
                "first_name": "Jogi",
                "last_name": "Löw",
                "gender": "M",
                "year": 1960,
                "class_": "Class 1",
                "club": "",
                "chip": "1234",
                "fields": {},
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH, time=2233
                ),
            },
        ],
    )
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year == 1960
    assert c[0].chip == ""

    assert c[1].first_name == "Angela"
    assert c[1].last_name == "Merkel"
    assert c[1].club_id == club_id
    assert c[1].club_name == "OL Bundestag"
    assert c[1].gender == "F"
    assert c[1].year == 1957
    assert c[1].chip == "9999999"

    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 2

    assert data[0]["id"] != data[1]["id"]

    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Jogi"
    assert data[0]["last_name"] == "Löw"
    assert data[0]["gender"] == "M"
    assert data[0]["year"] == 1960
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "1234"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH, time=2233
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"

    assert data[1]["event_id"] == event_2_id
    assert data[1]["first_name"] == "Angela"
    assert data[1]["last_name"] == "Merkel"
    assert data[1]["gender"] == "F"
    assert data[1]["year"] == 1957
    assert data[1]["not_competing"] is True
    assert data[1]["chip"] == "4455"
    assert data[1]["fields"] == {0: "x"}
    assert data[1]["result"] == result_type.PersonRaceResult(
        status=ResultStatus.OK, time=2361
    )
    assert data[1]["start"] == start_type.PersonRaceStart(start_time=S3)
    assert data[1]["club_id"] == club_id
    assert data[1]["club"] == "OL Bundestag"
    assert data[1]["class_id"] == class_1_id
    assert data[1]["class_"] == "Class 1"


def test_import_entries_with_results(db, event_2_id, class_1_id):
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "",
                "chip": "4455",
                "result": result_type.PersonRaceResult(
                    start_time=datetime.datetime(
                        2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                    ),
                    finish_time=datetime.datetime(
                        2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                    ),
                    status=ResultStatus.OK,
                    time=2001,
                    split_times=[
                        result_type.SplitTime(control_code="31", status="OK", time=501),
                        result_type.SplitTime(control_code="32", status="OK", time=720),
                        result_type.SplitTime(control_code="31", status="OK", time=818),
                        result_type.SplitTime(
                            control_code="33", status="OK", time=1136
                        ),
                        result_type.SplitTime(
                            control_code="31", status="OK", time=1593
                        ),
                    ],
                ),
            },
        ],
    )
    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 1

    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Angela"
    assert data[0]["last_name"] == "Merkel"
    assert data[0]["gender"] == ""
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "4455"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        start_time=datetime.datetime(
            2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
        ),
        finish_time=datetime.datetime(
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
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"


def test_import_entries_already_exist_with_results(db, event_2_id, class_1_id):
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "",
                "chip": "4455",
                "result": result_type.PersonRaceResult(
                    start_time=datetime.datetime(
                        2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
                    ),
                    finish_time=datetime.datetime(
                        2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
                    ),
                    status=ResultStatus.OK,
                    time=2001,
                    split_times=[
                        result_type.SplitTime(control_code="31", status="OK", time=501),
                        result_type.SplitTime(control_code="32", status="OK", time=720),
                        result_type.SplitTime(control_code="31", status="OK", time=818),
                        result_type.SplitTime(
                            control_code="33", status="OK", time=1136
                        ),
                        result_type.SplitTime(
                            control_code="31", status="OK", time=1593
                        ),
                    ],
                ),
            },
        ],
    )
    db.import_entries(
        event_id=event_2_id,
        entries=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "class_": "Class 1",
                "club": "",
                "chip": "1324",
                "result": result_type.PersonRaceResult(
                    start_time=datetime.datetime(
                        2020, 2, 9, 10, 5, 0, tzinfo=timezone(timedelta(hours=1))
                    ),
                    finish_time=None,
                    status=ResultStatus.MISSING_PUNCH,
                    time=1753,
                    split_times=[
                        result_type.SplitTime(control_code="31", status="OK", time=333),
                        result_type.SplitTime(control_code="34", status="OK", time=720),
                        result_type.SplitTime(
                            control_code="31", status="Missing", time=None
                        ),
                        result_type.SplitTime(
                            control_code="33", status="OK", time=1136
                        ),
                        result_type.SplitTime(
                            control_code="31", status="OK", time=1593
                        ),
                    ],
                ),
            },
        ],
    )

    data = list(db.get_entries(event_id=event_2_id))
    assert len(data) == 1

    assert data[0]["event_id"] == event_2_id
    assert data[0]["first_name"] == "Angela"
    assert data[0]["last_name"] == "Merkel"
    assert data[0]["gender"] == ""
    assert data[0]["year"] is None
    assert data[0]["not_competing"] is False
    assert data[0]["chip"] == "1324"
    assert data[0]["fields"] == {}
    assert data[0]["result"] == result_type.PersonRaceResult(
        start_time=datetime.datetime(
            2020, 2, 9, 10, 5, 0, tzinfo=timezone(timedelta(hours=1))
        ),
        finish_time=None,
        status=ResultStatus.MISSING_PUNCH,
        time=1753,
        split_times=[
            result_type.SplitTime(control_code="31", status="OK", time=333),
            result_type.SplitTime(control_code="34", status="OK", time=720),
            result_type.SplitTime(control_code="31", status="Missing", time=None),
            result_type.SplitTime(control_code="33", status="OK", time=1136),
            result_type.SplitTime(control_code="31", status="OK", time=1593),
        ],
    )
    assert data[0]["start"] == start_type.PersonRaceStart()
    assert data[0]["club_id"] is None
    assert data[0]["club"] is None
    assert data[0]["class_id"] == class_1_id
    assert data[0]["class_"] == "Class 1"

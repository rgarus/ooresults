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
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.club_type import ClubType
from ooresults.repo.competitor_type import CompetitorType
from ooresults.repo.entry_type import EntryType
from ooresults.repo import result_type
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SpStatus
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
        fields=[],
    )


@pytest.fixture
def event_2_id(db):
    return db.add_event(
        name="event 2",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
        fields=[],
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
    db,
    event_2_id,
    entry_1_id,
    entry_2_id,
    entry_3_id,
    club_id,
    class_2_id,
):
    c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
    c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=False,
        chip="",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.INACTIVE),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_get_first_added_entry(
    db, event_2_id, club_id, class_2_id, entry_1_id, entry_2_id, entry_3_id
):
    competitor = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    assert competitor == CompetitorType(
        id=competitor.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="9999999",
        club_id=club_id,
        club_name="OL Bundestag",
    )

    data = db.get_entry(id=entry_2_id)
    assert data == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=competitor.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_get_last_added_entry(
    db, event_2_id, club_id, class_2_id, entry_1_id, entry_2_id, entry_3_id
):
    competitor = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
    assert competitor == CompetitorType(
        id=competitor.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        chip="",
        club_id=None,
        club_name=None,
    )

    data = db.get_entry(id=entry_3_id)
    assert data == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=competitor.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=False,
        chip="",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.INACTIVE),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )


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
    c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
    c2 = db.get_competitor_by_name(first_name="angela", last_name="merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=False,
        chip="",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.INACTIVE),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c2.id,
        first_name="angela",
        last_name="merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="7788",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
        start=start_type.PersonRaceStart(start_time=S2),
        club_id=None,
        club_name=None,
    )


def test_update_result_first_added_entry(
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    db.update_entry_result(
        id=entry_2_id,
        chip="7788",
        start_time=S2,
        result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
    )
    c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
    c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=False,
        chip="",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.INACTIVE),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="7788",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
        start=start_type.PersonRaceStart(start_time=S2),
        club_id=club_id,
        club_name="OL Bundestag",
    )


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
    c1 = db.get_competitor_by_name(first_name="jogi", last_name="Loew")
    c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="jogi",
        last_name="Loew",
        gender="M",
        year=1960,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(S3),
        club_id=club_id,
        club_name="OL Bundestag",
    )
    assert data[1] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_update_result_last_added_entry(
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    db.update_entry_result(
        id=entry_3_id,
        chip="4455",
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start_time=S3,
    )
    c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
    c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=False,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(S3),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_add_existing_competitor_but_do_not_update_competitors_chip_and_club_if_alread_defined(
    db, event_1_id, class_1_id, competitor_1_id, club_id
):
    entry_id = db.add_entry(
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
    data = db.get_entries(event_id=event_1_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=entry_id,
        event_id=event_1_id,
        competitor_id=competitor_1_id,
        first_name="Angela",
        last_name="Merkel",
        gender="W",
        year=None,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="999",
        fields={},
        result=result_type.PersonRaceResult(),
        start=start_type.PersonRaceStart(),
        club_id=club_id,
        club_name="OL Bundestag",
    )

    data = db.get_competitor(id=competitor_1_id)
    assert data == CompetitorType(
        id=competitor_1_id,
        first_name="Angela",
        last_name="Merkel",
        gender="W",
        year=None,
        chip="1234567",
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_add_existing_competitor_and_update_competitors_chip_and_club_if_undefined(
    db, event_1_id, class_1_id, competitor_2_id, club_id
):
    entry_id = db.add_entry(
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
    data = db.get_entries(event_id=event_1_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=entry_id,
        event_id=event_1_id,
        competitor_id=competitor_2_id,
        first_name="Yogi",
        last_name="Löw",
        gender="M",
        year=1975,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="999",
        fields={},
        result=result_type.PersonRaceResult(),
        start=start_type.PersonRaceStart(),
        club_id=club_id,
        club_name="OL Bundestag",
    )

    data = db.get_competitor(id=competitor_2_id)
    assert data == CompetitorType(
        id=competitor_2_id,
        first_name="Yogi",
        last_name="Löw",
        gender="M",
        year=1975,
        chip="999",
        club_id=club_id,
        club_name="OL Bundestag",
    )


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

    c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 3

    assert data[0] == EntryType(
        id=entry_id_2_result,
        event_id=event_2_id,
        competitor_id=None,
        first_name=None,
        last_name=None,
        gender=None,
        year=None,
        class_id=None,
        class_name=None,
        not_competing=False,
        chip="2289",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.MISSING_PUNCH),
        start=start_type.PersonRaceStart(start_time=S2),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=entry_id_1_result,
        event_id=event_2_id,
        competitor_id=None,
        first_name=None,
        last_name=None,
        gender=None,
        year=None,
        class_id=None,
        class_name=None,
        not_competing=False,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S3),
        club_id=None,
        club_name=None,
    )
    assert data[2] == EntryType(
        id=entry_2_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_2_id,
        class_name="Class 2",
        not_competing=True,
        chip="9999999",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


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
    classes = db.get_classes(event_id=event_2_id)
    assert len(classes) == 2
    assert classes[0].id != classes[1].id

    assert classes[0] == ClassInfoType(
        id=classes[0].id,
        name="Class 1",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )
    assert classes[1] == ClassInfoType(
        id=classes[1].id,
        name="Class 2",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    clubs = db.get_clubs()
    assert len(clubs) == 1

    assert ClubType(
        id=clubs[0].id,
        name="OL Bundestag",
    )

    c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=1960,
        chip="1234",
    )
    assert c[1] == CompetitorType(
        id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        club_id=clubs[0].id,
        club_name=clubs[0].name,
        gender="",
        year=None,
        chip="4455",
    )

    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2
    assert data[0].id != data[1].id

    assert data[0] == EntryType(
        id=data[0].id,
        event_id=event_2_id,
        competitor_id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=1960,
        class_id=classes[1].id,
        class_name=classes[1].name,
        not_competing=False,
        chip="1234",
        fields={},
        result=result_type.PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH, time=2233
        ),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=data[1].id,
        event_id=event_2_id,
        competitor_id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=classes[0].id,
        class_name=classes[0].name,
        not_competing=True,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.OK, time=2361),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=clubs[0].id,
        club_name=clubs[0].name,
    )


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
    c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=1960,
        chip="1234",
    )
    assert c[1] == CompetitorType(
        id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="",
        year=None,
        chip="4455",
    )

    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2
    assert data[0].id != data[1].id

    assert data[0] == EntryType(
        id=data[0].id,
        event_id=event_2_id,
        competitor_id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=1960,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="1234",
        fields={},
        result=result_type.PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH, time=2233
        ),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=data[1].id,
        event_id=event_2_id,
        competitor_id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(status=ResultStatus.OK, time=2361),
        start=start_type.PersonRaceStart(start_time=S1),
        club_id=club_id,
        club_name="OL Bundestag",
    )


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
    c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=1960,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="9999999",
    )

    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 2
    assert data[0].id != data[1].id

    assert data[0] == EntryType(
        id=data[0].id,
        event_id=event_2_id,
        competitor_id=c[0].id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=1960,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="1234",
        fields={},
        result=result_type.PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH, time=2233
        ),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    assert data[1] == EntryType(
        id=data[1].id,
        event_id=event_2_id,
        competitor_id=c[1].id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=True,
        chip="4455",
        fields={0: "x"},
        result=result_type.PersonRaceResult(status=ResultStatus.OK, time=2361),
        start=start_type.PersonRaceStart(start_time=S3),
        club_id=club_id,
        club_name="OL Bundestag",
    )


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
            },
        ],
    )

    c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=data[0].id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="4455",
        fields={},
        result=result_type.PersonRaceResult(
            start_time=datetime.datetime(
                2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
            ),
            finish_time=datetime.datetime(
                2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
            ),
            status=ResultStatus.OK,
            time=2001,
            split_times=[
                result_type.SplitTime(control_code="31", status=SpStatus.OK, time=501),
                result_type.SplitTime(control_code="32", status=SpStatus.OK, time=720),
                result_type.SplitTime(control_code="31", status=SpStatus.OK, time=818),
                result_type.SplitTime(control_code="33", status=SpStatus.OK, time=1136),
                result_type.SplitTime(control_code="31", status=SpStatus.OK, time=1593),
            ],
        ),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )


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
                        result_type.SplitTime(
                            control_code="31", status=SpStatus.OK, time=333
                        ),
                        result_type.SplitTime(
                            control_code="34", status=SpStatus.OK, time=720
                        ),
                        result_type.SplitTime(
                            control_code="31", status=SpStatus.MISSING, time=None
                        ),
                        result_type.SplitTime(
                            control_code="33", status=SpStatus.OK, time=1136
                        ),
                        result_type.SplitTime(
                            control_code="31", status=SpStatus.OK, time=1593
                        ),
                    ],
                ),
            },
        ],
    )

    c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = db.get_entries(event_id=event_2_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=data[0].id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        class_name="Class 1",
        not_competing=False,
        chip="1324",
        fields={},
        result=result_type.PersonRaceResult(
            start_time=datetime.datetime(
                2020, 2, 9, 10, 5, 0, tzinfo=timezone(timedelta(hours=1))
            ),
            finish_time=None,
            status=ResultStatus.MISSING_PUNCH,
            time=1753,
            split_times=[
                result_type.SplitTime(control_code="31", status=SpStatus.OK, time=333),
                result_type.SplitTime(control_code="34", status=SpStatus.OK, time=720),
                result_type.SplitTime(
                    control_code="31", status=SpStatus.MISSING, time=None
                ),
                result_type.SplitTime(control_code="33", status=SpStatus.OK, time=1136),
                result_type.SplitTime(control_code="31", status=SpStatus.OK, time=1593),
            ],
        ),
        start=start_type.PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

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
from collections.abc import Iterator
from datetime import timedelta
from datetime import timezone

import pytest

from ooresults import model
from ooresults.otypes import result_type
from ooresults.otypes import start_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SpStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo.sqlite_repo import SqliteRepo


S1 = datetime.datetime(2021, 8, 19, 18, 43, 33, tzinfo=timezone(timedelta(hours=2)))
S2 = datetime.datetime(2021, 8, 18, 17, 55, 00, tzinfo=timezone(timedelta(hours=2)))
S3 = datetime.datetime(2021, 8, 17, 10, 12, 14, tzinfo=timezone(timedelta(hours=2)))


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


@pytest.fixture
def event_1_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_event(
            name="event 1",
            date=datetime.date(year=2020, month=1, day=1),
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


@pytest.fixture
def event_2_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_event(
            name="event 2",
            date=datetime.date(year=2020, month=1, day=1),
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


@pytest.fixture
def class_1_id(db: SqliteRepo, event_2_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_2_id,
            name="Class 1",
            short_name=None,
            course_id=None,
            params=ClassParams(),
        )


@pytest.fixture
def class_2_id(db: SqliteRepo, event_2_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_2_id,
            name="Class 2",
            short_name=None,
            course_id=None,
            params=ClassParams(),
        )


@pytest.fixture
def club_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_club(
            name="OL Bundestag",
        )


@pytest.fixture
def competitor_1_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Robert",
            last_name="Lewandowski",
            club_id=None,
            gender="",
            year=None,
            chip="",
        )


@pytest.fixture
def competitor_2_id(db: SqliteRepo, club_id: int) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=club_id,
            gender="F",
            year=1957,
            chip="1234567",
        )


@pytest.fixture
def competitor_3_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Jogi",
            last_name="Löw",
            club_id=None,
            gender="M",
            year=None,
            chip="",
        )


@pytest.fixture
def entry_1_id(
    db: SqliteRepo, event_1_id: int, class_1_id: int, club_id: int, competitor_1_id: int
) -> int:
    with db.transaction():
        return db.add_entry(
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=False,
            chip="9999999",
            fields={0: "ab", 1: "cd"},
            result=PersonRaceResult(),
            start=PersonRaceStart(),
        )


@pytest.fixture
def entry_2_id(
    db: SqliteRepo, event_2_id: int, class_2_id: int, club_id: int, competitor_2_id: int
) -> int:
    with db.transaction():
        return db.add_entry(
            event_id=event_2_id,
            competitor_id=competitor_2_id,
            class_id=class_2_id,
            club_id=club_id,
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S1),
        )


@pytest.fixture
def entry_3_id(
    db: SqliteRepo, event_2_id: int, class_2_id: int, competitor_3_id: int
) -> int:
    with db.transaction():
        return db.add_entry(
            event_id=event_2_id,
            competitor_id=competitor_3_id,
            class_id=class_2_id,
            club_id=None,
            not_competing=False,
            chip="",
            fields={},
            result=PersonRaceResult(),
            start=PersonRaceStart(),
        )


def test_import_entries_empty_db(db: SqliteRepo, event_2_id: int):
    model.entries.import_entries(
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
    classes = model.classes.get_classes(event_id=event_2_id)
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

    clubs = model.clubs.get_clubs()
    assert len(clubs) == 1

    assert ClubType(
        id=clubs[0].id,
        name="OL Bundestag",
    )

    c = model.competitors.get_competitors()
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

    data = model.entries.get_entries(event_id=event_2_id)
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


def test_import_entries(db: SqliteRepo, event_2_id: int, class_1_id: int, club_id: int):
    model.entries.import_entries(
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
    c = model.competitors.get_competitors()
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

    data = model.entries.get_entries(event_id=event_2_id)
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
    db: SqliteRepo,
    event_2_id: int,
    class_1_id: int,
    club_id: int,
    entry_2_id: int,
    entry_3_id: int,
):
    model.entries.import_entries(
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
    c = model.competitors.get_competitors()
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
        chip="1234567",
    )

    data = model.entries.get_entries(event_id=event_2_id)
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


def test_import_entries_with_results(db: SqliteRepo, event_2_id: int, class_1_id: int):
    model.entries.import_entries(
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

    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = model.entries.get_entries(event_id=event_2_id)
    assert c1 is not None
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


def test_import_entries_already_exist_with_results(
    db: SqliteRepo, event_2_id: int, class_1_id: int
):
    model.entries.import_entries(
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
    model.entries.import_entries(
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

    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    data = model.entries.get_entries(event_id=event_2_id)
    assert c1 is not None
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

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

from ooresults.otypes import result_type
from ooresults.otypes import start_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.entry_type import EntryBaseDataType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo.sqlite_repo import SqliteRepo


S1 = datetime.datetime(2021, 8, 19, 18, 43, 33, tzinfo=timezone(timedelta(hours=2)))
S2 = datetime.datetime(2021, 8, 18, 17, 55, 00, tzinfo=timezone(timedelta(hours=2)))
S3 = datetime.datetime(2021, 8, 17, 10, 12, 14, tzinfo=timezone(timedelta(hours=2)))


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    _db = SqliteRepo(db=":memory:")
    yield _db
    _db.close()


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


def test_add_entry(
    db: SqliteRepo, event_1_id: int, class_1_id: int, club_id: int, competitor_1_id: int
):
    with db.transaction():
        id = db.add_entry(
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S1),
        )

    with db.transaction():
        data = db.get_entries(event_id=event_1_id)
    assert data == [
        EntryType(
            id=id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_add_entry_two_same_entries(
    db: SqliteRepo, event_1_id: int, class_1_id: int, club_id: int, competitor_1_id: int
):
    with db.transaction():
        id1 = db.add_entry(
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S1),
        )
    with db.transaction():
        id2 = db.add_entry(
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S1),
        )
    assert id1 != id2

    with db.transaction():
        data = db.get_entries(event_id=event_1_id)
    assert (
        data[0].id != data[1].id
        and data[0].id in [id1, id2]
        and data[1].id in [id1, id2]
    )
    assert data == [
        EntryType(
            id=data[0].id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
        EntryType(
            id=data[1].id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_add_many_entries(
    db: SqliteRepo, event_1_id: int, class_1_id: int, club_id: int, competitor_1_id: int
):
    with db.transaction():
        db.add_many_entries(
            [
                EntryBaseDataType(
                    event_id=event_1_id,
                    competitor_id=competitor_1_id,
                    class_id=class_1_id,
                    club_id=club_id,
                    not_competing=True,
                    chip="9999999",
                    fields={0: "x"},
                    result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
                    start=PersonRaceStart(start_time=S1),
                )
            ]
        )

    with db.transaction():
        data = db.get_entries(event_id=event_1_id)
    assert data == [
        EntryType(
            id=data[0].id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_add_many_entries_two_same_entries(
    db: SqliteRepo, event_1_id: int, class_1_id: int, club_id: int, competitor_1_id: int
):
    with db.transaction():
        db.add_many_entries(
            [
                EntryBaseDataType(
                    event_id=event_1_id,
                    competitor_id=competitor_1_id,
                    class_id=class_1_id,
                    club_id=club_id,
                    not_competing=True,
                    chip="9999999",
                    fields={0: "x"},
                    result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
                    start=PersonRaceStart(start_time=S1),
                ),
                EntryBaseDataType(
                    event_id=event_1_id,
                    competitor_id=competitor_1_id,
                    class_id=class_1_id,
                    club_id=club_id,
                    not_competing=True,
                    chip="9999999",
                    fields={0: "x"},
                    result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
                    start=PersonRaceStart(start_time=S1),
                ),
            ]
        )

    with db.transaction():
        data = db.get_entries(event_id=event_1_id)
    assert data[0].id != data[1].id
    assert data == [
        EntryType(
            id=data[0].id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
        EntryType(
            id=data[1].id,
            event_id=event_1_id,
            competitor_id=competitor_1_id,
            first_name="Robert",
            last_name="Lewandowski",
            gender="",
            year=None,
            class_id=class_1_id,
            class_name="Class 1",
            not_competing=True,
            chip="9999999",
            fields={0: "x"},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S1),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_get_entries(
    db,
    event_2_id,
    entry_1_id,
    entry_2_id,
    entry_3_id,
    club_id,
    class_2_id,
):
    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
        c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)
    assert c1 is not None and c2 is not None
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
    with db.transaction():
        competitor = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    assert competitor == CompetitorType(
        id=competitor.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="1234567",
        club_id=club_id,
        club_name="OL Bundestag",
    )

    with db.transaction():
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
    with db.transaction():
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

    with db.transaction():
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
    db, event_2_id, class_1_id, class_2_id, club_id, entry_2_id, entry_3_id
):
    with db.transaction():
        db.update_entry(
            id=entry_2_id,
            class_id=class_1_id,
            club_id=None,
            not_competing=False,
            chip="7788",
            fields={},
            result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
            start=start_type.PersonRaceStart(start_time=S2),
        )

    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
        c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)

    assert c1 == CompetitorType(
        id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        chip="",
        club_id=None,
        club_name=None,
    )
    assert c2 == CompetitorType(
        id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="1234567",
        club_id=club_id,
        club_name="OL Bundestag",
    )
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
    with db.transaction():
        db.update_entry_result(
            id=entry_2_id,
            chip="7788",
            result=result_type.PersonRaceResult(status=ResultStatus.DISQUALIFIED),
            start=PersonRaceStart(start_time=S2),
        )
    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
        c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)
    assert c1 is not None and c2 is not None
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
    with db.transaction():
        db.update_entry(
            id=entry_3_id,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=False,
            chip="4455",
            fields={},
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=start_type.PersonRaceStart(start_time=S3),
        )
    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
        c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)

    assert c1 == CompetitorType(
        id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        chip="",
        club_id=None,
        club_name=None,
    )
    assert c2 == CompetitorType(
        id=c2.id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="1234567",
        club_id=club_id,
        club_name="OL Bundestag",
    )
    assert len(data) == 2

    assert data[0] == EntryType(
        id=entry_3_id,
        event_id=event_2_id,
        competitor_id=c1.id,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
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
    with db.transaction():
        db.update_entry_result(
            id=entry_3_id,
            chip="4455",
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S3),
        )
    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Jogi", last_name="Löw")
        c2 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)
    assert c1 is not None and c2 is not None
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


def test_add_entry_result(db, event_2_id, class_2_id, club_id, entry_2_id):
    with db.transaction():
        entry_id_1_result = db.add_entry_result(
            event_id=event_2_id,
            chip="4455",
            result=result_type.PersonRaceResult(status=ResultStatus.DID_NOT_START),
            start=PersonRaceStart(start_time=S3),
        )
        entry_id_2_result = db.add_entry_result(
            event_id=event_2_id,
            chip="2289",
            result=result_type.PersonRaceResult(status=ResultStatus.MISSING_PUNCH),
            start=PersonRaceStart(start_time=S2),
        )

    with db.transaction():
        c1 = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
        data = db.get_entries(event_id=event_2_id)
    assert c1 is not None
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

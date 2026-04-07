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

import pytest

from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.competitor_type import CompetitorBaseDataType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo import repo
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    _db = SqliteRepo(db=":memory:")
    yield _db
    _db.close()


@pytest.fixture
def club_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_club(
            name="OL Bundestag",
        )


@pytest.fixture
def event_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_event(
            name="Event",
            date=datetime.date(year=2020, month=1, day=1),
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


@pytest.fixture
def class_id(db: SqliteRepo, event_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_id,
            name="Class",
            short_name=None,
            course_id=None,
            params=ClassParams(),
        )


@pytest.fixture
def entry_id(db: SqliteRepo, event_id: int, class_id: int, competitor_1_id: int) -> int:
    with db.transaction():
        return db.add_entry(
            event_id=event_id,
            competitor_id=competitor_1_id,
            class_id=class_id,
            club_id=None,
            not_competing=False,
            chip="",
            fields={},
            result=PersonRaceResult(),
            start=PersonRaceStart(),
        )


@pytest.fixture
def competitor_1_id(db: SqliteRepo, club_id: int) -> int:
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


def test_get_competitors_after_adding_one_competitor(
    db: SqliteRepo, competitor_1_id: int, club_id: int
):
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 1
    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_get_competitors_after_adding_two_competitors(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_get_first_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        c = db.get_competitor(id=competitor_1_id)
    assert c == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_get_last_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        c = db.get_competitor(id=competitor_2_id)
    assert c == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_get_competitor_by_name(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        c = db.get_competitor_by_name(first_name="Angela", last_name="Merkel")
    assert c == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_if_no_item_found_then_get_competitor_by_name_returns_none(
    db, competitor_1_id: int
):
    with db.transaction():
        c = db.get_competitor_by_name(first_name="abc", last_name="def")
    assert c is None


def test_update_first_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        db.update_competitor(
            id=competitor_1_id,
            first_name="Anton",
            last_name="Berkel",
            club_id=club_id,
            gender="M",
            year=1958,
            chip="",
        )
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Anton",
        last_name="Berkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="M",
        year=1958,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_update_last_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        db.update_competitor(
            id=competitor_2_id,
            first_name="Anton",
            last_name="Berkel",
            club_id=None,
            gender="M",
            year=1958,
            chip="",
        )
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=competitor_2_id,
        first_name="Anton",
        last_name="Berkel",
        club_id=None,
        club_name=None,
        gender="M",
        year=1958,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_add_competitor_with_same_first_name(
    db: SqliteRepo, competitor_1_id: int, club_id: int
):
    with db.transaction():
        competitor_2_id = db.add_competitor(
            first_name="Jogi",
            last_name="Berkel",
            club_id=None,
            gender="M",
            year=1958,
            chip="",
        )
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=competitor_2_id,
        first_name="Jogi",
        last_name="Berkel",
        club_id=None,
        club_name=None,
        gender="M",
        year=1958,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_add_competitor_with_same_last_name(
    db: SqliteRepo, competitor_1_id: int, club_id: int
):
    with db.transaction():
        competitor_2_id = db.add_competitor(
            first_name="Norbert",
            last_name="Löw",
            club_id=None,
            gender="M",
            year=1958,
            chip="",
        )
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )
    assert c[1] == CompetitorType(
        id=competitor_2_id,
        first_name="Norbert",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=1958,
        chip="",
    )


def test_delete_first_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        db.delete_competitor(id=competitor_1_id)
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 1
    assert c[0] == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_delete_last_added_competitor(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    with db.transaction():
        db.delete_competitor(id=competitor_2_id)
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 1
    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_add_existing_name_raises_exception(db: SqliteRepo, competitor_1_id: int):
    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        with db.transaction():
            db.add_competitor(
                first_name="Jogi",
                last_name="Löw",
                club_id=None,
                gender="M",
                year=1958,
                chip="",
            )


def test_add_many(db: SqliteRepo, club_id: int):
    with db.transaction():
        db.add_many_competitors(
            [
                CompetitorBaseDataType(
                    first_name="Angela",
                    last_name="Merkel",
                    club_id=club_id,
                    gender="F",
                    year=1957,
                    chip="123",
                ),
                CompetitorBaseDataType(
                    first_name="Jogi",
                    last_name="Löw",
                    club_id=None,
                    gender="M",
                    year=None,
                    chip="456",
                ),
            ],
        )
    with db.transaction():
        c = db.get_competitors()
    assert c == [
        CompetitorType(
            id=c[0].id,
            first_name="Jogi",
            last_name="Löw",
            club_id=None,
            club_name=None,
            gender="M",
            year=None,
            chip="456",
        ),
        CompetitorType(
            id=c[1].id,
            first_name="Angela",
            last_name="Merkel",
            club_id=club_id,
            club_name="OL Bundestag",
            gender="F",
            year=1957,
            chip="123",
        ),
    ]


def test_add_many_with_existing_name_raises_exception(
    db: SqliteRepo, competitor_1_id: int
):
    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        with db.transaction():
            db.add_many_competitors(
                [
                    CompetitorBaseDataType(
                        first_name="Angela",
                        last_name="Merkel",
                        club_id=None,
                        gender="F",
                        year=None,
                        chip="",
                    ),
                    CompetitorBaseDataType(
                        first_name="Jogi",
                        last_name="Löw",
                        club_id=None,
                        gender="M",
                        year=1958,
                        chip="",
                    ),
                ],
            )
    with db.transaction():
        c = db.get_competitors()
    assert c == [
        CompetitorType(
            id=competitor_1_id,
            first_name="Jogi",
            last_name="Löw",
            club_id=None,
            club_name=None,
            gender="M",
            year=None,
            chip="",
        )
    ]


def test_add_with_not_existing_club_id_raises_exception(db: SqliteRepo):
    with pytest.raises(repo.ConstraintError, match="Club id does not exist"):
        with db.transaction():
            db.add_competitor(
                first_name="Jogi",
                last_name="Löw",
                club_id=999,
                gender="M",
                year=1958,
                chip="",
            )


def test_change_to_existing_name_raises_exception(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int
):
    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        with db.transaction():
            db.update_competitor(
                id=competitor_1_id,
                first_name="Angela",
                last_name="Merkel",
                club_id=None,
                gender="F",
                year=None,
                chip="",
            )


def test_update_with_unknown_id_raises_exception(db: SqliteRepo, competitor_1_id: int):
    with pytest.raises(KeyError):
        with db.transaction():
            db.update_competitor(
                id=competitor_1_id + 1,
                first_name="Anton",
                last_name="Berkel",
                club_id=None,
                gender="M",
                year=1958,
                chip="",
            )


def test_delete_competitor_with_unknown_id_do_not_change_anything(
    db: SqliteRepo, competitor_1_id: int
):
    with db.transaction():
        db.delete_competitor(id=competitor_1_id + 1)
    with db.transaction():
        c = db.get_competitors()
    assert len(c) == 1
    assert c[0] == CompetitorType(
        id=competitor_1_id,
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        club_name=None,
        gender="M",
        year=None,
        chip="",
    )


def test_delete_competitor_used_in_entry_raises_exception(
    db: SqliteRepo, entry_id: int, competitor_1_id: int
):
    with pytest.raises(repo.CompetitorUsedError):
        with db.transaction():
            db.delete_competitor(id=competitor_1_id)

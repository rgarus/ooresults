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

from ooresults import model
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.competitor_type import Sex
from ooresults.otypes.entry_type import EntryBaseDataType
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


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
def class_1_id(db: SqliteRepo, event_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_id,
            name="Elite",
            short_name="E",
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
def competitor_1_id(db: SqliteRepo, club_id: int) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=club_id,
            sex=Sex.FEMALE,
            year=1957,
            chip="1234567",
        )


@pytest.fixture
def competitor_2_id(db: SqliteRepo, club_id: int) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Angel",
            last_name="Merkel",
            club_id=club_id,
            sex=Sex.MALE,
            year=None,
            chip="55555",
        )


@pytest.fixture
def competitor_3_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Jogi",
            last_name="Löw",
            club_id=None,
            sex=Sex.MALE,
            year=None,
            chip="",
        )


@pytest.mark.parametrize(
    "old, new",
    [
        (3, 2),
        (1, 3),
        (2, 1),
    ],
)
def test_merge_competitor(
    old: int,
    new: int,
    db: SqliteRepo,
    event_id: int,
    club_id: int,
    competitor_1_id: int,
    competitor_2_id: int,
    competitor_3_id: int,
    class_1_id: int,
) -> None:
    c_id = {1: competitor_1_id, 2: competitor_2_id, 3: competitor_3_id}

    with db.transaction():
        db.add_many_entries(
            [
                EntryBaseDataType(
                    event_id=event_id,
                    competitor_id=competitor_1_id,
                    class_id=class_1_id,
                ),
                EntryBaseDataType(
                    event_id=event_id,
                    competitor_id=competitor_1_id,
                    class_id=class_1_id,
                ),
                EntryBaseDataType(
                    event_id=event_id,
                    competitor_id=competitor_2_id,
                    class_id=class_1_id,
                ),
            ]
        )

    with db.transaction():
        entries_old = db.get_entries(event_id=event_id)
        competitor = db.get_competitor(id=c_id[new])
        competitors_old = db.get_competitors()

    model.competitors.merge_competitor(id_old=c_id[old], id_new=c_id[new])

    with db.transaction():
        entries_new = db.get_entries(event_id=event_id)
        competitors_new = db.get_competitors()

    for entry in entries_old:
        if entry.competitor_id == c_id[old]:
            entry.competitor_id = competitor.id
            entry.last_name = competitor.last_name
            entry.first_name = competitor.first_name
            entry.sex = competitor.sex
            entry.year = competitor.year

    entries_old.sort(key=lambda e: e.id)
    entries_new.sort(key=lambda e: e.id)
    assert entries_new == entries_old
    assert competitors_new == [c for c in competitors_old if c.id != c_id[old]]

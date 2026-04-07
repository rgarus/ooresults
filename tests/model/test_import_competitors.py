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


from collections.abc import Iterator

import pytest

from ooresults import model
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


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


def test_import_competitors(db: SqliteRepo):
    model.competitors.import_competitors(
        competitors=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "club": "OL Bundestag",
                "chip": "",
            },
            {
                "first_name": "Jogi",
                "last_name": "Löw",
                "gender": "M",
                "year": 1960,
                "club": "",
                "chip": "1234",
            },
        ],
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
        chip="",
    )


def test_import_competitors_new_competitors_are_added(
    db: SqliteRepo, competitor_1_id: int, competitor_2_id: int, club_id: int
):
    model.competitors.import_competitors(
        competitors=[
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "F",
                "year": 1958,
                "club": "OL Bundestag",
                "chip": "4455",
            },
        ],
    )
    clubs = model.clubs.get_clubs()
    assert len(clubs) == 1

    assert ClubType(
        id=club_id,
        name="OL Bundestag",
    )

    c = model.competitors.get_competitors()
    assert len(c) == 3
    assert c[0].id != c[1].id
    assert c[0].id != c[2].id
    assert c[1].id != c[2].id

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
    assert c[2] == CompetitorType(
        id=c[2].id,
        first_name="Birgit",
        last_name="Merkel",
        club_id=club_id,
        club_name="OL Bundestag",
        gender="F",
        year=1958,
        chip="4455",
    )


def test_import_competitors_imported_values_overwrite_existing_values(
    db: SqliteRepo, competitor_2_id: int, club_id: int
):
    model.competitors.import_competitors(
        competitors=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "M",
                "year": 2001,
                "club": "Team Angela",
                "chip": "4455",
            },
        ],
    )
    clubs = model.clubs.get_clubs()
    assert len(clubs) == 2
    assert clubs[0].id != clubs[1].id

    assert clubs[0] == ClubType(
        id=club_id,
        name="OL Bundestag",
    )
    assert clubs[1] == ClubType(
        id=clubs[1].id,
        name="Team Angela",
    )

    c = model.competitors.get_competitors()
    assert len(c) == 1

    assert c[0] == CompetitorType(
        id=competitor_2_id,
        first_name="Angela",
        last_name="Merkel",
        club_id=clubs[1].id,
        club_name="Team Angela",
        gender="M",
        year=2001,
        chip="4455",
    )


def test_import_competitors_missing_values_do_not_change_anything(
    db: SqliteRepo, competitor_2_id: int, club_id: int
):
    model.competitors.import_competitors(
        competitors=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": None,
                "club": "",
                "chip": "",
            },
        ],
    )
    clubs = model.clubs.get_clubs()
    assert len(clubs) == 1

    assert clubs[0] == ClubType(
        id=club_id,
        name="OL Bundestag",
    )

    c = model.competitors.get_competitors()
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

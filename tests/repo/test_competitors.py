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

import pytest

from ooresults.repo import repo
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo.club_type import ClubType
from ooresults.repo.competitor_type import CompetitorType
from ooresults.repo.result_type import ResultStatus


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def club_id(db):
    return db.add_club(
        name="OL Bundestag",
    )


@pytest.fixture
def event_id(db):
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
        fields=[],
    )


@pytest.fixture
def class_id(db, event_id):
    return db.add_class(
        event_id=event_id,
        name="Class",
        short_name=None,
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def entry_id(db, event_id, class_id, competitor_1_id):
    return db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Jogi",
        last_name="Löw",
        gender="M",
        year=None,
        class_id=class_id,
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )


@pytest.fixture
def competitor_1_id(db, club_id):
    return db.add_competitor(
        first_name="Jogi",
        last_name="Löw",
        club_id=None,
        gender="M",
        year=None,
        chip="",
    )


@pytest.fixture
def competitor_2_id(db, club_id):
    return db.add_competitor(
        first_name="Angela",
        last_name="Merkel",
        club_id=club_id,
        gender="F",
        year=1957,
        chip="1234567",
    )


def test_get_competitors_after_adding_one_competitor(db, competitor_1_id, club_id):
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
    db, competitor_1_id, competitor_2_id, club_id
):
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


def test_get_first_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
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


def test_get_last_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
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


def test_get_competitor_by_name(db, competitor_1_id, competitor_2_id, club_id):
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


def test_update_first_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.update_competitor(
        id=competitor_1_id,
        first_name="Anton",
        last_name="Berkel",
        club_id=club_id,
        gender="M",
        year=1958,
        chip="",
    )
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


def test_update_last_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.update_competitor(
        id=competitor_2_id,
        first_name="Anton",
        last_name="Berkel",
        club_id=None,
        gender="M",
        year=1958,
        chip="",
    )
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


def test_add_competitor_with_same_first_name(db, competitor_1_id, club_id):
    competitor_2_id = db.add_competitor(
        first_name="Jogi",
        last_name="Berkel",
        club_id=None,
        gender="M",
        year=1958,
        chip="",
    )
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


def test_add_competitor_with_same_last_name(db, competitor_1_id, club_id):
    competitor_2_id = db.add_competitor(
        first_name="Norbert",
        last_name="Löw",
        club_id=None,
        gender="M",
        year=1958,
        chip="",
    )
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


def test_delete_first_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.delete_competitor(id=competitor_1_id)
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


def test_delete_last_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.delete_competitor(id=competitor_2_id)
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


def test_add_existing_name_raises_exception(db, competitor_1_id):
    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        db.add_competitor(
            first_name="Jogi",
            last_name="Löw",
            club_id=None,
            gender="M",
            year=1958,
            chip="",
        )


def test_change_to_existing_name_raises_exception(db, competitor_1_id, competitor_2_id):
    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        db.update_competitor(
            id=competitor_1_id,
            first_name="Angela",
            last_name="Merkel",
            club_id=None,
            gender="F",
            year=None,
            chip="",
        )


def test_update_with_unknown_id_raises_exception(db, competitor_1_id):
    with pytest.raises(KeyError):
        db.update_competitor(
            id=competitor_1_id + 1,
            first_name="Anton",
            last_name="Berkel",
            club_id=None,
            gender="M",
            year=1958,
            chip="",
        )


def test_delete_competitor_with_unknown_id_do_not_change_anything(db, competitor_1_id):
    db.delete_competitor(id=competitor_1_id + 1)
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
    db, entry_id, competitor_1_id
):
    with pytest.raises(repo.CompetitorUsedError):
        db.delete_competitor(id=competitor_1_id)


def test_import_competitors(db):
    db.import_competitors(
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
        chip="",
    )


def test_import_competitors_new_competitors_are_added(
    db, competitor_1_id, competitor_2_id, club_id
):
    db.import_competitors(
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
    clubs = db.get_clubs()
    assert len(clubs) == 1

    assert ClubType(
        id=club_id,
        name="OL Bundestag",
    )

    c = db.get_competitors()
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
    db, competitor_2_id, club_id
):
    db.import_competitors(
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
    clubs = db.get_clubs()
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

    c = db.get_competitors()
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
    db, competitor_2_id, club_id
):
    db.import_competitors(
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
    clubs = db.get_clubs()
    assert len(clubs) == 1

    assert clubs[0] == ClubType(
        id=club_id,
        name="OL Bundestag",
    )

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

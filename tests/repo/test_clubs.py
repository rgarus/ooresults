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
from ooresults.repo.result_type import ResultStatus


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def club_1_id(db):
    return db.add_club(
        name="Club 1",
    )


@pytest.fixture
def club_2_id(db):
    return db.add_club(
        name="Club 2",
    )


@pytest.fixture
def competitor_id(db, club_1_id):
    return db.add_competitor(
        first_name="A",
        last_name="B",
        club_id=club_1_id,
        gender="",
        year=None,
        chip="",
    )


@pytest.fixture
def event_id(db):
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
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
def entry_id(db, event_id, class_id, club_1_id):
    return db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="A",
        last_name="B",
        gender="",
        year=None,
        class_id=class_id,
        club_id=club_1_id,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )


def test_get_clubs_after_adding_one_club(db, club_1_id):
    c = list(db.get_clubs())
    assert len(c) == 1
    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"


def test_get_clubs_after_adding_two_clubs(db, club_1_id, club_2_id):
    c = list(db.get_clubs())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"
    assert c[1].id == club_2_id
    assert c[1].name == "Club 2"


def test_get_first_added_club(db, club_1_id, club_2_id):
    c = list(db.get_club(id=club_1_id))
    assert len(c) == 1
    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"


def test_get_last_added_club(db, club_1_id, club_2_id):
    c = list(db.get_club(id=club_2_id))
    assert len(c) == 1
    assert c[0].id == club_2_id
    assert c[0].name == "Club 2"


def test_update_first_added_club(db, club_1_id, club_2_id):
    db.update_club(id=club_1_id, name="Club 3")
    c = list(db.get_clubs())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == club_2_id
    assert c[0].name == "Club 2"
    assert c[1].id == club_1_id
    assert c[1].name == "Club 3"


def test_update_last_added_club(db, club_1_id, club_2_id):
    db.update_club(id=club_2_id, name="Club 3")
    c = list(db.get_clubs())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"
    assert c[1].id == club_2_id
    assert c[1].name == "Club 3"


def test_delete_first_added_club(db, club_1_id, club_2_id):
    db.delete_club(id=club_1_id)
    c = list(db.get_clubs())
    assert len(c) == 1
    assert c[0].id == club_2_id
    assert c[0].name == "Club 2"


def test_delete_last_added_club(db, club_1_id, club_2_id):
    db.delete_club(id=club_2_id)
    c = list(db.get_clubs())
    assert len(c) == 1
    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"


def test_add_existing_name_raises_exception(db, club_1_id):
    with pytest.raises(repo.ConstraintError, match="Club already exist"):
        db.add_club(name="Club 1")


def test_change_to_existing_name_raises_exception(db, club_1_id, club_2_id):
    with pytest.raises(repo.ConstraintError, match="Club already exist"):
        db.update_club(id=club_1_id, name="Club 2")


def test_update_with_unknown_id_raises_exception(db, club_1_id):
    with pytest.raises(KeyError):
        db.update_club(id=club_1_id + 1, name="Club 2")


def test_delete_club_with_unknown_id_do_not_change_anything(db, club_1_id):
    db.delete_club(id=club_1_id + 1)
    c = list(db.get_clubs())
    assert len(c) == 1
    assert c[0].id == club_1_id
    assert c[0].name == "Club 1"


def test_delete_club_used_in_competitor_raises_exception(db, competitor_id, club_1_id):
    with pytest.raises(repo.ClubUsedError):
        db.delete_club(id=club_1_id)


def test_delete_club_used_in_entry_raises_exception(db, entry_id, club_1_id):
    with pytest.raises(repo.ClubUsedError):
        db.delete_club(id=club_1_id)

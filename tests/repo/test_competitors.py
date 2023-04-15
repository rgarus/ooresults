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
    c = list(db.get_competitors())
    assert len(c) == 1
    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""


def test_get_competitors_after_adding_two_competitors(
    db, competitor_1_id, competitor_2_id, club_id
):
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""
    assert c[1].id == competitor_2_id
    assert c[1].first_name == "Angela"
    assert c[1].last_name == "Merkel"
    assert c[1].club_id == club_id
    assert c[1].club_name == "OL Bundestag"
    assert c[1].gender == "F"
    assert c[1].year == 1957
    assert c[1].chip == "1234567"


def test_get_first_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    c = list(db.get_competitor(id=competitor_1_id))
    assert len(c) == 1
    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""


def test_get_last_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    c = list(db.get_competitor(id=competitor_2_id))
    assert len(c) == 1
    assert c[0].id == competitor_2_id
    assert c[0].first_name == "Angela"
    assert c[0].last_name == "Merkel"
    assert c[0].club_id == club_id
    assert c[0].gender == "F"
    assert c[0].year == 1957
    assert c[0].chip == "1234567"


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
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Anton"
    assert c[0].last_name == "Berkel"
    assert c[0].club_id == club_id
    assert c[0].club_name == "OL Bundestag"
    assert c[0].gender == "M"
    assert c[0].year == 1958
    assert c[0].chip == ""
    assert c[1].id == competitor_2_id
    assert c[1].first_name == "Angela"
    assert c[1].last_name == "Merkel"
    assert c[1].club_id == club_id
    assert c[1].club_name == "OL Bundestag"
    assert c[1].gender == "F"
    assert c[1].year == 1957
    assert c[1].chip == "1234567"


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
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == competitor_2_id
    assert c[0].first_name == "Anton"
    assert c[0].last_name == "Berkel"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year == 1958
    assert c[0].chip == ""
    assert c[1].id == competitor_1_id
    assert c[1].first_name == "Jogi"
    assert c[1].last_name == "Löw"
    assert c[1].club_id is None
    assert c[1].club_name is None
    assert c[1].gender == "M"
    assert c[1].year is None
    assert c[1].chip == ""


def test_add_competitor_with_same_first_name(db, competitor_1_id, club_id):
    competitor_2_id = db.add_competitor(
        first_name="Jogi",
        last_name="Berkel",
        club_id=None,
        gender="M",
        year=1958,
        chip="",
    )
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == competitor_2_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Berkel"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year == 1958
    assert c[0].chip == ""
    assert c[1].id == competitor_1_id
    assert c[1].first_name == "Jogi"
    assert c[1].last_name == "Löw"
    assert c[1].club_id is None
    assert c[1].club_name is None
    assert c[1].gender == "M"
    assert c[1].year is None
    assert c[1].chip == ""


def test_add_competitor_with_same_last_name(db, competitor_1_id, club_id):
    competitor_2_id = db.add_competitor(
        first_name="Norbert",
        last_name="Löw",
        club_id=None,
        gender="M",
        year=1958,
        chip="",
    )
    c = list(db.get_competitors())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""
    assert c[1].id == competitor_2_id
    assert c[1].first_name == "Norbert"
    assert c[1].last_name == "Löw"
    assert c[1].club_id is None
    assert c[1].club_name is None
    assert c[1].gender == "M"
    assert c[1].year == 1958
    assert c[1].chip == ""


def test_delete_first_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.delete_competitor(id=competitor_1_id)
    c = list(db.get_competitors())
    assert len(c) == 1
    assert c[0].id == competitor_2_id
    assert c[0].first_name == "Angela"
    assert c[0].last_name == "Merkel"
    assert c[0].club_id == club_id
    assert c[0].club_name == "OL Bundestag"
    assert c[0].gender == "F"
    assert c[0].year == 1957
    assert c[0].chip == "1234567"


def test_delete_last_added_competitor(db, competitor_1_id, competitor_2_id, club_id):
    db.delete_competitor(id=competitor_2_id)
    c = list(db.get_competitors())
    assert len(c) == 1
    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""


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
    c = list(db.get_competitors())
    assert len(c) == 1
    assert c[0].id == competitor_1_id
    assert c[0].first_name == "Jogi"
    assert c[0].last_name == "Löw"
    assert c[0].club_id is None
    assert c[0].club_name is None
    assert c[0].gender == "M"
    assert c[0].year is None
    assert c[0].chip == ""


def test_delete_competitor_used_in_entry_raises_exception(
    db, entry_id, competitor_1_id
):
    with pytest.raises(repo.CompetitorUsedError):
        db.delete_competitor(id=competitor_1_id)

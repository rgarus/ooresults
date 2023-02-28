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


D_2021_03_02 = datetime.date(year=2021, month=3, day=2)
D_2021_03_18 = datetime.date(year=2021, month=3, day=18)
D_2020_02_14 = datetime.date(year=2020, month=2, day=14)
D_2020_02_03 = datetime.date(year=2020, month=2, day=3)


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def event_1_id(db):
    return db.add_event(
        name="XX",
        date=D_2021_03_02,
        key="4711",
        publish=False,
        series="Run 1",
        fields=[],
    )


@pytest.fixture
def event_2_id(db):
    return db.add_event(
        name="YY",
        date=D_2021_03_18,
        key=None,
        publish=True,
        series=None,
        fields=["f1", "f2"],
    )


def test_get_events_after_adding_one_event(db, event_1_id):
    c = list(db.get_events())
    assert len(c) == 1
    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []


def test_get_events_after_adding_two_events(db, event_1_id, event_2_id):
    c = list(db.get_events())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []
    assert c[1].id == event_2_id
    assert c[1].name == "YY"
    assert c[1].date == D_2021_03_18
    assert c[1].key is None
    assert c[1].publish is True
    assert c[1].series is None
    assert c[1].fields == ["f1", "f2"]


def test_get_first_added_event(db, event_1_id, event_2_id):
    c = list(db.get_event(id=event_1_id))
    assert len(c) == 1
    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []


def test_get_last_added_event(db, event_1_id, event_2_id):
    c = list(db.get_event(id=event_2_id))
    assert len(c) == 1
    assert c[0].id == event_2_id
    assert c[0].name == "YY"
    assert c[0].date == D_2021_03_18
    assert c[0].key is None
    assert c[0].publish is True
    assert c[0].series is None
    assert c[0].fields == ["f1", "f2"]


def test_update_first_added_event(db, event_1_id, event_2_id):
    db.update_event(
        id=event_1_id,
        name="ZZ",
        date=D_2020_02_14,
        key=None,
        publish=True,
        series=None,
        fields=["x"],
    )
    c = list(db.get_events())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == event_2_id
    assert c[0].name == "YY"
    assert c[0].date == D_2021_03_18
    assert c[0].key is None
    assert c[0].publish is True
    assert c[0].series is None
    assert c[0].fields == ["f1", "f2"]
    assert c[1].id == event_1_id
    assert c[1].name == "ZZ"
    assert c[1].date == D_2020_02_14
    assert c[1].key is None
    assert c[1].publish is True
    assert c[1].series is None
    assert c[1].fields == ["x"]


def test_update_last_added_event(db, event_1_id, event_2_id):
    db.update_event(
        id=event_2_id,
        name="ZZ",
        date=D_2020_02_14,
        key="0000",
        publish=False,
        series="Run 1",
        fields=["x"],
    )
    c = list(db.get_events())
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []
    assert c[1].id == event_2_id
    assert c[1].name == "ZZ"
    assert c[1].date == D_2020_02_14
    assert c[1].key == "0000"
    assert c[1].publish is False
    assert c[1].series == "Run 1"
    assert c[1].fields == ["x"]


def test_delete_first_added_event(db, event_1_id, event_2_id):
    db.delete_event(id=event_1_id)
    c = list(db.get_events())
    assert len(c) == 1
    assert c[0].id == event_2_id
    assert c[0].name == "YY"
    assert c[0].date == D_2021_03_18
    assert c[0].key is None
    assert c[0].publish is True
    assert c[0].series is None
    assert c[0].fields == ["f1", "f2"]


def test_delete_last_added_event(db, event_1_id, event_2_id):
    db.delete_event(id=event_2_id)
    c = list(db.get_events())
    assert len(c) == 1
    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []


def test_add_existing_name_raises_exception(db, event_1_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.add_event(
            name="XX", date=D_2020_02_03, key=None, publish=False, series=False
        )


def test_add_existing_key_raises_exception(db, event_1_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.add_event(
            name="ZZ", date=D_2020_02_03, key="4711", publish=True, series=False
        )


def test_change_to_existing_name_raises_exception(db, event_1_id, event_2_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.update_event(
            id=event_1_id,
            name="YY",
            date=D_2020_02_03,
            key=None,
            publish=False,
            series=True,
        )


def test_change_to_existing_key_raises_exception(db, event_1_id, event_2_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.update_event(
            id=event_2_id,
            name="ZZ",
            date=D_2020_02_03,
            key="4711",
            publish=True,
            series=True,
        )


def test_update_with_unknown_id_raises_exception(db, event_1_id):
    with pytest.raises(KeyError):
        db.update_event(
            id=event_1_id + 1,
            name="YY",
            date=D_2020_02_03,
            key=None,
            publish=False,
            series=False,
        )


def test_delete_event_with_unknown_id_do_not_change_anything(db, event_1_id):
    db.delete_event(id=event_1_id + 1)
    c = list(db.get_events())
    assert len(c) == 1
    assert c[0].id == event_1_id
    assert c[0].name == "XX"
    assert c[0].date == D_2021_03_02
    assert c[0].key == "4711"
    assert c[0].publish is False
    assert c[0].series == "Run 1"
    assert c[0].fields == []

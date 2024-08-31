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
from ooresults.repo.event_type import EventType


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
    c = db.get_events()
    assert c == [
        EventType(
            id=event_1_id,
            name="XX",
            date=D_2021_03_02,
            key="4711",
            publish=False,
            series="Run 1",
            fields=[],
        ),
    ]


def test_get_events_after_adding_two_events(db, event_1_id, event_2_id):
    c = db.get_events()
    assert c[0].id != c[1].id

    assert c == [
        EventType(
            id=event_1_id,
            name="XX",
            date=D_2021_03_02,
            key="4711",
            publish=False,
            series="Run 1",
            fields=[],
        ),
        EventType(
            id=event_2_id,
            name="YY",
            date=D_2021_03_18,
            key=None,
            publish=True,
            series=None,
            fields=["f1", "f2"],
        ),
    ]


def test_get_first_added_event(db, event_1_id, event_2_id):
    c = db.get_event(id=event_1_id)
    assert c == EventType(
        id=event_1_id,
        name="XX",
        date=D_2021_03_02,
        key="4711",
        publish=False,
        series="Run 1",
        fields=[],
    )


def test_get_last_added_event(db, event_1_id, event_2_id):
    c = db.get_event(id=event_2_id)
    assert c == EventType(
        id=event_2_id,
        name="YY",
        date=D_2021_03_18,
        key=None,
        publish=True,
        series=None,
        fields=["f1", "f2"],
    )


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
    c = db.get_events()
    assert c[0].id != c[1].id

    assert c == [
        EventType(
            id=event_2_id,
            name="YY",
            date=D_2021_03_18,
            key=None,
            publish=True,
            series=None,
            fields=["f1", "f2"],
        ),
        EventType(
            id=event_1_id,
            name="ZZ",
            date=D_2020_02_14,
            key=None,
            publish=True,
            series=None,
            fields=["x"],
        ),
    ]


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
    c = db.get_events()
    assert c[0].id != c[1].id

    assert c == [
        EventType(
            id=event_1_id,
            name="XX",
            date=D_2021_03_02,
            key="4711",
            publish=False,
            series="Run 1",
            fields=[],
        ),
        EventType(
            id=event_2_id,
            name="ZZ",
            date=D_2020_02_14,
            key="0000",
            publish=False,
            series="Run 1",
            fields=["x"],
        ),
    ]


def test_delete_first_added_event(db, event_1_id, event_2_id):
    db.delete_event(id=event_1_id)
    c = db.get_events()
    assert c == [
        EventType(
            id=event_2_id,
            name="YY",
            date=D_2021_03_18,
            key=None,
            publish=True,
            series=None,
            fields=["f1", "f2"],
        ),
    ]


def test_delete_last_added_event(db, event_1_id, event_2_id):
    db.delete_event(id=event_2_id)
    c = db.get_events()
    assert c == [
        EventType(
            id=event_1_id,
            name="XX",
            date=D_2021_03_02,
            key="4711",
            publish=False,
            series="Run 1",
            fields=[],
        ),
    ]


def test_add_existing_name_raises_exception(db, event_1_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.add_event(
            name="XX",
            date=D_2020_02_03,
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


def test_add_existing_key_raises_exception(db, event_1_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.add_event(
            name="ZZ",
            date=D_2020_02_03,
            key="4711",
            publish=True,
            series=None,
            fields=[],
        )


def test_change_to_existing_name_raises_exception(db, event_1_id, event_2_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.update_event(
            id=event_1_id,
            name="YY",
            date=D_2020_02_03,
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


def test_change_to_existing_key_raises_exception(db, event_1_id, event_2_id):
    with pytest.raises(repo.ConstraintError, match="Event or event key already exist"):
        db.update_event(
            id=event_2_id,
            name="ZZ",
            date=D_2020_02_03,
            key="4711",
            publish=True,
            series=None,
            fields=[],
        )


def test_update_with_unknown_id_raises_exception(db, event_1_id):
    with pytest.raises(KeyError):
        db.update_event(
            id=event_1_id + 1,
            name="YY",
            date=D_2020_02_03,
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


def test_get_event_with_unknown_id_raises_exception(db, event_1_id):
    with pytest.raises(repo.EventNotFoundError):
        db.get_event(id=event_1_id + 1)


def test_delete_event_with_unknown_id_do_not_change_anything(db, event_1_id):
    db.delete_event(id=event_1_id + 1)
    c = db.get_events()
    assert c == [
        EventType(
            id=event_1_id,
            name="XX",
            date=D_2021_03_02,
            key="4711",
            publish=False,
            series="Run 1",
            fields=[],
        ),
    ]

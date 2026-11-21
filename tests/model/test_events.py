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


import copy
import datetime
from collections.abc import Iterator

import pytest

from ooresults import model
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


@pytest.fixture
def event_1(db: SqliteRepo) -> EventType:
    with db.transaction():
        id = db.add_event(
            name="Event 1",
            date=datetime.date(year=2015, month=1, day=1),
            key="4711",
            publish=False,
            series=None,
            fields=[],
        )
        item = db.get_event(id=id)
        return copy.deepcopy(item)


@pytest.fixture
def event_2(db: SqliteRepo) -> EventType:
    with db.transaction():
        id = db.add_event(
            name="Event 2",
            date=datetime.date(year=2015, month=1, day=1),
            key="5757",
            publish=False,
            series=None,
            fields=[],
        )
        item = db.get_event(id=id)
        return copy.deepcopy(item)


def test_get_event_by_event_key_4711(
    db: SqliteRepo, event_1: EventType, event_2: EventType
) -> None:
    event = model.events.get_event_by_event_key(event_key="4711")
    assert event == event_1


def test_get_event_by_event_key_5757(
    db: SqliteRepo, event_1: EventType, event_2: EventType
) -> None:
    event = model.events.get_event_by_event_key(event_key="5757")
    assert event == event_2


def test_get_event_by_event_key_raises_exception_if_event_not_found(
    db: SqliteRepo, event_1: EventType, event_2: EventType
) -> None:
    with pytest.raises(EventNotFoundError, match='Event for key "local" not found'):
        model.events.get_event_by_event_key(event_key="local")

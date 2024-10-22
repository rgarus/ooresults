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


import asyncio
import datetime
from unittest.mock import AsyncMock

import pytest

from ooresults.repo.event_type import EventType
from ooresults.websocket_server.streaming_status import Status
from ooresults.websocket_server.streaming_status import StreamingStatus


@pytest.fixture
def status_1() -> StreamingStatus:
    s = StreamingStatus()
    s.status = {
        2: Status.ERROR,
        4: Status.SERVER_NOT_REACHABLE,
    }
    return s


@pytest.fixture
def status_2() -> StreamingStatus:
    s = StreamingStatus()
    s.status = {
        2: Status.ERROR,
        3: Status.OK,
        4: Status.SERVER_NOT_REACHABLE,
    }
    return s


@pytest.fixture
def event() -> EventType:
    return EventType(
        id=3,
        name="ABC",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
        fields=[],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )


def test_get_status(status_1):
    assert status_1.get(id=2) == Status.ERROR


def test_set_status(status_1, event):
    asyncio.run(status_1.set(event=event, status=Status.OK))
    assert status_1.status == {
        2: Status.ERROR,
        3: Status.OK,
        4: Status.SERVER_NOT_REACHABLE,
    }


def test_update_status(status_2, event):
    asyncio.run(status_2.set(event=event, status=Status.ACCESS_DENIED))
    assert status_2.status == {
        2: Status.ERROR,
        3: Status.ACCESS_DENIED,
        4: Status.SERVER_NOT_REACHABLE,
    }


def test_delete_status(status_2, event):
    asyncio.run(status_2.delete(event=event))
    assert status_2.status == {
        2: Status.ERROR,
        4: Status.SERVER_NOT_REACHABLE,
    }


def test_register_awaitable(status_1):
    a = AsyncMock()

    status_1.register(awaitable=a)
    assert status_1.awaitable == a


def test_if_set_is_called_then_awaitable_is_called(status_1, event):
    a = AsyncMock()

    status_1.register(awaitable=a)
    asyncio.run(status_1.set(event=event, status=Status.OK))
    a.assert_awaited_once_with(event)


def test_if_delete_is_called_then_awaitable_is_called(status_1, event):
    a = AsyncMock()

    status_1.register(awaitable=a)
    asyncio.run(status_1.delete(event=event))
    a.assert_awaited_once_with(event)


def test_awaitable_not_called_after_register_none(status_1, event):
    a = AsyncMock()

    status_1.register(awaitable=a)
    status_1.register(awaitable=None)
    asyncio.run(status_1.set(event=event, status=Status.OK))
    a.assert_not_awaited()

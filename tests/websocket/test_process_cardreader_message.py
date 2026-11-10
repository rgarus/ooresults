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


import bz2
import datetime
import json
from collections.abc import Iterator

import pytest

from ooresults import model
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.websocket_server.websocket_handler import WebSocketHandler


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


@pytest.fixture
def event(db: SqliteRepo) -> EventType:
    with db.transaction():
        id = db.add_event(
            name="Event",
            date=datetime.date(year=2015, month=1, day=1),
            key="local",
            publish=False,
            series=None,
            fields=[],
        )
        return db.get_event(id=id)


def test_process_message(
    event: EventType,
) -> None:
    item = {
        "entryType": "readerDisconnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    result = ("readerDisconnected", event, {"eventId": event.id})
    assert result == WebSocketHandler().process_cardreader_message(
        message=bz2.compress(json.dumps(item).encode()),
        event_key="local",
    )


def test_if_event_not_found_then_an_event_not_found_error_is_raised(
    event: EventType,
) -> None:
    item = {
        "entryType": "readerDisconnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    with pytest.raises(EventNotFoundError):
        WebSocketHandler().process_cardreader_message(
            message=bz2.compress(json.dumps(item).encode()),
            event_key="12345",
        )


def test_if_message_is_not_bz2_compressed_then_an_exception_is_raised(
    event: EventType,
) -> None:
    item = {
        "entryType": "readerDisconnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    with pytest.raises(RuntimeError, match="Data not bz2 compressed"):
        WebSocketHandler().process_cardreader_message(
            message=json.dumps(item).encode(),
            event_key="local",
        )


def test_if_decompressed_message_is_too_large_then_an_exception_is_raised(
    event: EventType,
) -> None:
    with pytest.raises(RuntimeError, match="Data too large"):
        WebSocketHandler().process_cardreader_message(
            message=bz2.compress(100_001 * b"0"),
            event_key="local",
        )


def test_if_decompressed_message_is_not_utf8_encoded_then_an_exception_is_raised(
    event: EventType,
) -> None:
    with pytest.raises(RuntimeError, match="Data not utf-8 encoded"):
        WebSocketHandler().process_cardreader_message(
            message=bz2.compress('"öäü"'.encode(encoding="latin")),
            event_key="local",
        )


def test_if_decompressed_message_is_not_json_deserialisable_then_an_exception_is_raised(
    event: EventType,
) -> None:
    with pytest.raises(RuntimeError, match="Data not json deserialisable"):
        WebSocketHandler().process_cardreader_message(
            message=bz2.compress(b"abc"),
            event_key="local",
        )


def test_if_decompressed_message_is_not_a_cardreader_message_then_an_exception_is_raised(
    event: EventType,
) -> None:
    with pytest.raises(RuntimeError, match="'abc' is not of type"):
        WebSocketHandler().process_cardreader_message(
            message=bz2.compress(b'"abc"'),
            event_key="local",
        )

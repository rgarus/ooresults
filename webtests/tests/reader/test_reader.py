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
import pathlib

import jsonschema

import ooresults
from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.webclient import WebSocketClient


data_path = (
    pathlib.Path(ooresults.__file__).resolve().parent / "schema" / "cardreader_log.json"
)
with open(data_path) as file:
    schema_cardreader_log = json.loads(file.read())


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-01-23"
KEY = "local"


def test_if_reader_client_is_not_connected_then_reader_status_is_offline(
    main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Offline")


def test_if_reader_client_is_stopped_then_reader_status_is_offline(
    main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    client = WebSocketClient(key=KEY)
    try:
        client.start()
        wait.until(lambda _: client.opened)

        # send status
        item = {
            "entryType": "readerDisconnected",
            "entryTime": datetime.datetime.now().astimezone().isoformat(),
        }
        jsonschema.validate(instance=item, schema=schema_cardreader_log)
        client.send(bz2.compress(json.dumps(item).encode()))

        # receive and check answer
        result = client.receive(timeout=10)
        assert len(result) == 3
        assert result["readerStatus"] == "readerDisconnected"
        assert result["event"] == event
        assert result["eventId"] > 0

        wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
        wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
        wait.until(lambda _: reader_page.get_reader_status() == "Disconnected")

        client.reconnect = False
        if client.wsapp:
            client.wsapp.close()
        wait.until(lambda _: reader_page.get_reader_status() == "Offline")

    finally:
        client.reconnect = False
        if client.wsapp:
            client.wsapp.close()


def test_if_a_si_reader_unit_is_not_found_then_reader_status_is_disconnected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    # send status
    item = {
        "entryType": "readerDisconnected",
        "entryTime": datetime.datetime.now().astimezone().isoformat(),
    }
    jsonschema.validate(instance=item, schema=schema_cardreader_log)
    client.send(bz2.compress(json.dumps(item).encode()))

    # receive and check answer
    result = client.receive(timeout=10)
    assert len(result) == 3
    assert result["readerStatus"] == "readerDisconnected"
    assert result["event"] == EVENT_NAME
    assert result["eventId"] > 0

    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Disconnected")


def test_if_a_si_reader_unit_is_found_then_reader_status_is_connected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    # send status
    item = {
        "entryType": "readerConnected",
        "entryTime": datetime.datetime.now().astimezone().isoformat(),
    }
    jsonschema.validate(instance=item, schema=schema_cardreader_log)
    client.send(bz2.compress(json.dumps(item).encode()))

    # receive and check answer
    result = client.receive(timeout=10)
    assert len(result) == 3
    assert result["readerStatus"] == "readerConnected"
    assert result["event"] == EVENT_NAME
    assert result["eventId"] > 0

    # check status displayed at si reader page
    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Connected")


def test_if_a_si_card_is_inserted_then_reader_status_is_card_reading(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    # send status
    item = {
        "entryType": "cardInserted",
        "entryTime": datetime.datetime.now().astimezone().isoformat(),
        "controlCard": "7509749",
    }
    jsonschema.validate(instance=item, schema=schema_cardreader_log)
    client.send(bz2.compress(json.dumps(item).encode()))

    # receive and check answer
    result = client.receive(timeout=10)
    assert len(result) == 4
    assert result["readerStatus"] == "cardInserted"
    assert result["controlCard"] == "7509749"
    assert result["event"] == EVENT_NAME
    assert result["eventId"] > 0

    # check status displayed at si reader page
    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Reading card")


def test_if_a_si_card_is_removed_then_reader_status_is_connected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    # send status
    item = {
        "entryType": "cardRemoved",
        "entryTime": datetime.datetime.now().astimezone().isoformat(),
    }
    jsonschema.validate(instance=item, schema=schema_cardreader_log)
    client.send(bz2.compress(json.dumps(item).encode()))

    # receive and check answer
    result = client.receive(timeout=10)
    assert len(result) == 3
    assert result["readerStatus"] == "cardRemoved"
    assert result["event"] == EVENT_NAME
    assert result["eventId"] > 0

    # check status displayed at si reader page
    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Connected")


def test_if_a_si_card_is_read_then_reader_status_is_connected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    # send status
    item = {
        "entryType": "cardRead",
        "entryTime": datetime.datetime.now().astimezone().isoformat(),
        "controlCard": "7509749",
    }
    jsonschema.validate(instance=item, schema=schema_cardreader_log)
    client.send(bz2.compress(json.dumps(item).encode()))

    # receive and check answer
    result = client.receive(timeout=10)
    assert len(result) == 12
    assert result["readerStatus"] == "cardRead"
    assert result["controlCard"] == "7509749"
    assert result["event"] == EVENT_NAME
    assert result["eventId"] > 0
    assert result["entryTime"] is not None
    assert result["firstName"] is None
    assert result["lastName"] is None
    assert result["club"] is None
    assert result["class"] is None
    assert result["status"] == "INACTIVE"
    assert result["time"] is None
    assert result["error"] == "Control card unknown"

    # check status displayed at si reader page
    wait.until(lambda _: reader_page.get_event_name() == EVENT_NAME)
    wait.until(lambda _: reader_page.get_event_date() == EVENT_DATE)
    wait.until(lambda _: reader_page.get_reader_status() == "Connected")

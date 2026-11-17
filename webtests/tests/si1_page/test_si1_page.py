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
from collections.abc import Iterator

import jsonschema
import pytest

import ooresults
from webtests.pageobjects.entries import ImportEntryDialog
from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.si1_page import Si1Page
from webtests.pageobjects.webclient import WebSocketClient


data_path = (
    pathlib.Path(ooresults.__file__).resolve().parent / "schema" / "cardreader_log.json"
)
with open(data_path) as file:
    schema_cardreader_log = json.loads(file.read())


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-01-23"
KEY = "local"


@pytest.fixture(scope="module")
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture(scope="module")
def event(main_page: MainPage, delete_all: None) -> Iterator[str]:
    event_page = main_page.goto_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE, key=KEY)
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


@pytest.fixture(scope="module")
def entry_data(main_page: MainPage, event: str) -> None:
    entry_list_path = pathlib.Path(__file__).parent.parent / "data" / "EntryList.xml"
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    dialog.format().select(text=ImportEntryDialog.ENTRY_LIST)
    dialog.import_file(path=entry_list_path)


@pytest.fixture(scope="module")
def course_data(main_page: MainPage, event: str) -> None:
    course_data_path = pathlib.Path(__file__).parent.parent / "data" / "CourseData.xml"
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.import_()
    dialog.import_file(path=course_data_path)


@pytest.fixture()
def client(main_page: MainPage, event: str) -> Iterator[WebSocketClient]:
    websocket_client = WebSocketClient(key=KEY)
    try:
        websocket_client.start()
        main_page.wait(timeout=10).until(lambda _: websocket_client.opened)

        # send status
        item = {
            "entryType": "readerDisconnected",
            "entryTime": datetime.datetime.now().astimezone().isoformat(),
        }
        jsonschema.validate(instance=item, schema=schema_cardreader_log)
        websocket_client.send(bz2.compress(json.dumps(item).encode()))

        # receive and check answer
        result = websocket_client.receive(timeout=10)
        assert len(result) == 3
        assert result["readerStatus"] == "readerDisconnected"
        assert result["event"] == event
        assert result["eventId"] > 0
        yield websocket_client
    finally:
        websocket_client.reconnect = False
        if websocket_client.wsapp:
            websocket_client.wsapp.close()


def test_if_reader_client_is_not_connected_then_reader_status_is_offline(
    main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
        # check status displayed at si reader page
        wait.until(lambda _: si1_page.get_message() == "Card reader offline")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE
    finally:
        si1_page.close()


def test_if_reader_client_is_stopped_then_reader_status_is_offline(
    main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
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

        # check status displayed at si reader page
        wait.until(lambda _: si1_page.get_message() == "Card reader disconnected")

        client.reconnect = False
        if client.wsapp:
            client.wsapp.close()
        # check status displayed at si reader page
        wait.until(lambda _: si1_page.get_message() == "Card reader offline")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE

    finally:
        si1_page.close()
        client.reconnect = False
        if client.wsapp:
            client.wsapp.close()


def test_if_a_si_reader_unit_is_not_found_then_reader_status_is_disconnected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
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

        # check status displayed at si reader page
        wait.until(lambda _: si1_page.get_message() == "Card reader disconnected")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE
    finally:
        si1_page.close()


def test_if_a_si_reader_unit_is_found_then_reader_status_is_connected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
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
        wait.until(lambda _: si1_page.get_message() == "Card reader connected")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE
    finally:
        si1_page.close()


def test_if_a_si_card_is_inserted_then_reader_status_is_card_reading(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
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
        wait.until(lambda _: si1_page.get_message() == "Reading card 7509749 ...")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE
    finally:
        si1_page.close()


def test_if_a_si_card_is_removed_then_reader_status_is_connected(
    client: WebSocketClient, main_page: MainPage, event: str
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
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
        wait.until(lambda _: si1_page.get_message() == "Card reader connected")
        # check event name and date
        assert si1_page.get_event_name() == EVENT_NAME
        assert si1_page.get_event_date() == EVENT_DATE
    finally:
        si1_page.close()


def test_if_a_si_card_is_read_but_not_assigned_to_an_entry_then_an_unassigned_result_is_displayed(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
        # send status
        item = {
            "entryType": "cardRead",
            "entryTime": "2023-01-15T10:26:03.624810+01:00",
            "cardType": "SI10",
            "controlCard": "7000000",
            "startTime": "2023-01-15T10:10:00+01:00",
            "finishTime": "2023-01-15T10:24:39+01:00",
            "checkTime": "2023-01-15T10:00:00+01:00",
            "punches": [
                {"controlCode": "121", "punchTime": "2023-01-15T10:12:09+01:00"},
                {"controlCode": "124", "punchTime": "2023-01-15T10:15:25+01:00"},
                {"controlCode": "122", "punchTime": "2023-01-15T10:18:14+01:00"},
                {"controlCode": "123", "punchTime": "2023-01-15T10:22:00+01:00"},
            ],
        }
        jsonschema.validate(instance=item, schema=schema_cardreader_log)
        client.send(bz2.compress(json.dumps(item).encode()))

        # receive and check answer
        result = client.receive(timeout=10)
        assert len(result) == 12
        assert result["readerStatus"] == "cardRead"
        assert result["controlCard"] == "7000000"
        assert result["event"] == EVENT_NAME
        assert result["eventId"] > 0
        assert result["entryTime"] is not None
        assert result["firstName"] is None
        assert result["lastName"] is None
        assert result["club"] is None
        assert result["class"] is None
        assert result["status"] == "FINISHED"
        assert result["time"] is None
        assert result["error"] == "Control card unknown"

        # check result displayed at si reader page
        wait.until(lambda _: si1_page.get_line_1() == "7000000")
        wait.until(lambda _: si1_page.get_line_2() == "Control card unknown")
        wait.until(lambda _: si1_page.get_line_3() == "Bitte im WKZ melden")
        assert si1_page.get_background_color() == si1_page.YELLOW
    finally:
        si1_page.close()


def test_if_a_si_card_is_read_and_status_is_ok_then_result_is_displayed_as_ok(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
        # send status
        item = {
            "entryType": "cardRead",
            "entryTime": "2023-01-15T10:27:03.624810+01:00",
            "cardType": "SI10",
            "controlCard": "7379879",
            "startTime": "2023-01-15T10:10:00+01:00",
            "finishTime": "2023-01-15T10:24:39+01:00",
            "checkTime": "2023-01-15T10:00:00+01:00",
            "punches": [
                {"controlCode": "121", "punchTime": "2023-01-15T10:12:09+01:00"},
                {"controlCode": "124", "punchTime": "2023-01-15T10:15:25+01:00"},
                {"controlCode": "122", "punchTime": "2023-01-15T10:18:14+01:00"},
                {"controlCode": "123", "punchTime": "2023-01-15T10:22:00+01:00"},
            ],
        }
        jsonschema.validate(instance=item, schema=schema_cardreader_log)
        client.send(bz2.compress(json.dumps(item).encode()))

        # receive and check answer
        result = client.receive(timeout=10)
        assert len(result) == 13
        assert result["readerStatus"] == "cardRead"
        assert result["controlCard"] == "7379879"
        assert result["event"] == EVENT_NAME
        assert result["eventId"] > 0
        assert result["entryTime"] is not None
        assert result["firstName"] == "Annalena"
        assert result["lastName"] == "Baerbock"
        assert result["club"] == "OC Grün"
        assert result["class"] == "Bahn A - Frauen"
        assert result["status"] == "OK"
        assert result["time"] == 879
        assert result["missingControls"] == []
        assert result["error"] is None

        # check result displayed at si reader page
        wait.until(lambda _: si1_page.get_line_1() == "Baerbock, Annalena")
        wait.until(lambda _: si1_page.get_line_2() == "7379879, Bahn A - Frauen")
        wait.until(lambda _: si1_page.get_line_3() == "OK, 14:39 min")
        assert si1_page.get_background_color() == si1_page.GREEN
    finally:
        si1_page.close()


def test_if_a_si_card_is_read_and_status_is_not_ok_then_result_is_displayed_as_not_ok(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    si1_page = Si1Page(driver=main_page.driver)
    si1_page.open()
    try:
        # send status
        item = {
            "entryType": "cardRead",
            "entryTime": "2023-01-15T10:28:03.624810+01:00",
            "cardType": "SI10",
            "controlCard": "7509749",
            "startTime": "2023-01-15T10:12:00+01:00",
            "finishTime": "2023-01-15T10:26:04+01:00",
            "checkTime": "2023-01-15T10:08:30+01:00",
            "punches": [
                {"controlCode": "121", "punchTime": "2023-01-15T10:14:09+01:00"},
                {"controlCode": "124", "punchTime": "2023-01-15T10:19:00+01:00"},
                {"controlCode": "123", "punchTime": "2023-01-15T10:22:01+01:00"},
            ],
        }

        jsonschema.validate(instance=item, schema=schema_cardreader_log)
        client.send(bz2.compress(json.dumps(item).encode()))

        # receive and check answer
        result = client.receive(timeout=10)
        assert len(result) == 13
        assert result["readerStatus"] == "cardRead"
        assert result["controlCard"] == "7509749"
        assert result["event"] == EVENT_NAME
        assert result["eventId"] > 0
        assert result["entryTime"] is not None
        assert result["firstName"] == "Robert"
        assert result["lastName"] == "Habeck"
        assert result["club"] == "OC Grün"
        assert result["class"] == "Bahn A - Männer"
        assert result["status"] == "MISSING_PUNCH"
        assert result["time"] == 844
        assert result["missingControls"] == ["122"]
        assert result["error"] is None

        # check result displayed at si reader page
        wait.until(lambda _: si1_page.get_line_1() == "Habeck, Robert")
        wait.until(lambda _: si1_page.get_line_2() == "7509749, Bahn A - Männer")
        wait.until(lambda _: si1_page.get_line_3() == "MP")
        assert si1_page.get_background_color() == si1_page.RED
    finally:
        si1_page.close()

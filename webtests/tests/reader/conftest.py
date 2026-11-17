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

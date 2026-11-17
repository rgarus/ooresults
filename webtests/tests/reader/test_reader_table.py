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
import json
import pathlib

import jsonschema

import ooresults
from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.reader import ReaderTable
from webtests.pageobjects.table import RowIterator
from webtests.pageobjects.webclient import WebSocketClient


data_path = (
    pathlib.Path(ooresults.__file__).resolve().parent / "schema" / "cardreader_log.json"
)
with open(data_path) as file:
    schema_cardreader_log = json.loads(file.read())


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-01-23"
KEY = "local"


def test_if_reader_page_is_selected_then_the_table_header_is_displayed(
    main_page: MainPage, event: str
) -> None:
    reader_page = main_page.goto_reader(event=event)
    assert reader_page.table.nr_of_columns() == 7
    assert reader_page.table.headers() == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]


def get_rows(table: ReaderTable) -> list[str]:
    rows: list[str] = []
    for row in list(RowIterator(table=table)):
        rows.append(row)
    return rows


def test_if_a_si_card_is_read_but_not_assigned_to_an_entry_then_content_is_appended_to_table(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    existing_rows = get_rows(table=reader_page.table)
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

    # check table displayed at si reader page
    wait.until(lambda _: reader_page.table.nr_of_rows() == len(existing_rows) + 1)
    new_rows = get_rows(table=reader_page.table)
    assert len(new_rows) == len(existing_rows) + 1
    # existing rows are not changed
    assert new_rows[:-1] == existing_rows
    # new result is appended at the end of the table
    assert new_rows[-1] == [
        "10:26:03",
        "7000000",
        "Finished",
        "",
        "Control card unknown",
    ]
    color = reader_page.table.background_color_of_row(i=reader_page.table.nr_of_rows())
    assert color == reader_page.table.YELLOW


def test_if_a_si_card_is_read_and_status_is_ok_then_content_is_appended_to_table(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    existing_rows = get_rows(table=reader_page.table)
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

    # check table displayed at si reader page
    wait.until(lambda _: reader_page.table.nr_of_rows() == len(existing_rows) + 1)
    new_rows = get_rows(table=reader_page.table)
    assert len(new_rows) == len(existing_rows) + 1
    # existing rows are not changed
    assert new_rows[:-1] == existing_rows
    # new result is appended at the end of the table
    assert new_rows[-1] == [
        "10:27:03",
        "7379879",
        "OK",
        "14:39 min",
        "Baerbock, Annalena",
        "Bahn A - Frauen",
        "",
    ]
    color = reader_page.table.background_color_of_row(i=reader_page.table.nr_of_rows())
    assert color == reader_page.table.GREEN


def test_if_a_si_card_is_read_and_status_is_not_ok_then_content_is_appended_to_table(
    client: WebSocketClient,
    main_page: MainPage,
    event: str,
    entry_data: None,
    course_data: None,
) -> None:
    wait = main_page.wait(timeout=10)

    reader_page = main_page.goto_reader(event=event)
    existing_rows = get_rows(table=reader_page.table)
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

    # check table displayed at si reader page
    wait.until(lambda _: reader_page.table.nr_of_rows() == len(existing_rows) + 1)
    new_rows = get_rows(table=reader_page.table)
    assert len(new_rows) == len(existing_rows) + 1
    # existing rows are not changed
    assert new_rows[:-1] == existing_rows
    # new result is appended at the end of the table
    assert new_rows[-1] == [
        "10:28:03",
        "7509749",
        "MP",
        "14:04 min",
        "Habeck, Robert",
        "Bahn A - Männer",
        "122",
    ]
    color = reader_page.table.background_color_of_row(i=reader_page.table.nr_of_rows())
    assert color == reader_page.table.RED

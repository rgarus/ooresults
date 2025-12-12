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
from datetime import timezone

import pytest
from lxml import etree

from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.utils import render


@pytest.fixture()
def event() -> EventType:
    return EventType(
        id=3,
        name="Test-Lauf 1",
        date=datetime.date(
            year=2023,
            month=12,
            day=29,
        ),
        key=None,
        publish=False,
        series=None,
        fields=[],
    )


TABLE_ID = "entr.table"


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


@pytest.fixture()
def entry_full(event: EventType) -> EntryType:
    return EntryType(
        id=789,
        event_id=event.id,
        competitor_id=123,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=15,
        class_name="Elite Women",
        not_competing=True,
        chip="87121314",
        fields={0: "200"},
        result=PersonRaceResult(status=ResultStatus.FINISHED, time=417),
        start=PersonRaceStart(start_time=S1),
        club_id=415,
        club_name="OL Bundestag",
    )


def test_entry_list_with_view_is_entries(event: EventType, entry_full: EntryType):
    event.fields = ["Start number", "Region"]
    html = etree.HTML(
        render.entries_table(
            event=event, view="entries", view_entries_list=[(None, [entry_full])]
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    view = html.findall(".//select[@id='entr.view']/option")
    assert len(view) == 4
    assert view[0].attrib == {"value": "entries", "selected": "selected"}
    assert view[0].text == "Entries"
    assert view[1].attrib == {"value": "classes"}
    assert view[1].text == "Classes"
    assert view[2].attrib == {"value": "clubs"}
    assert view[2].text == "Clubs"
    assert view[3].attrib == {"value": "states"}
    assert view[3].text == "States"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Entries\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "X",
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
        "OL Bundestag",
        "Elite Women",
        "200",
        None,
        "12:38:59",
        "6:57",
        "Finished",
    ]


def test_entry_list_with_view_is_classes(event: EventType, entry_full: EntryType):
    event.fields = ["Start number", "Region"]
    html = etree.HTML(
        render.entries_table(
            event=event, view="classes", view_entries_list=[(None, [entry_full])]
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    view = html.findall(".//select[@id='entr.view']/option")
    assert len(view) == 4
    assert view[0].attrib == {"value": "entries"}
    assert view[0].text == "Entries"
    assert view[1].attrib == {"value": "classes", "selected": "selected"}
    assert view[1].text == "Classes"
    assert view[2].attrib == {"value": "clubs"}
    assert view[2].text == "Clubs"
    assert view[3].attrib == {"value": "states"}
    assert view[3].text == "States"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Unassigned results\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "X",
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
        "OL Bundestag",
        "200",
        None,
        "12:38:59",
        "6:57",
        "Finished",
    ]


def test_entry_list_with_view_is_clubs(event: EventType, entry_full: EntryType):
    event.fields = ["Start number", "Region"]
    html = etree.HTML(
        render.entries_table(
            event=event, view="clubs", view_entries_list=[(None, [entry_full])]
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    view = html.findall(".//select[@id='entr.view']/option")
    assert len(view) == 4
    assert view[0].attrib == {"value": "entries"}
    assert view[0].text == "Entries"
    assert view[1].attrib == {"value": "classes"}
    assert view[1].text == "Classes"
    assert view[2].attrib == {"value": "clubs", "selected": "selected"}
    assert view[2].text == "Clubs"
    assert view[3].attrib == {"value": "states"}
    assert view[3].text == "States"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Class",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Individuals/No club\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "X",
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
        "Elite Women",
        "200",
        None,
        "12:38:59",
        "6:57",
        "Finished",
    ]


def test_entry_list_with_view_is_states(event: EventType, entry_full: EntryType):
    event.fields = ["Start number", "Region"]
    html = etree.HTML(
        render.entries_table(
            event=event, view="states", view_entries_list=[(None, [entry_full])]
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    view = html.findall(".//select[@id='entr.view']/option")
    assert len(view) == 4
    assert view[0].attrib == {"value": "entries"}
    assert view[0].text == "Entries"
    assert view[1].attrib == {"value": "classes"}
    assert view[1].text == "Classes"
    assert view[2].attrib == {"value": "clubs"}
    assert view[2].text == "Clubs"
    assert view[3].attrib == {"value": "states", "selected": "selected"}
    assert view[3].text == "States"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Unassigned results\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "X",
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
        "OL Bundestag",
        "Elite Women",
        "200",
        None,
        "12:38:59",
        "6:57",
        "Finished",
    ]

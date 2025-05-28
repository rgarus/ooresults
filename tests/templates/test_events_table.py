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


from datetime import date
from typing import List
from typing import Optional

import pytest
from lxml import etree

from ooresults.otypes.event_type import EventType
from ooresults.utils import render


@pytest.fixture()
def events() -> List[EventType]:
    return [
        EventType(
            id=3,
            name="Test-Lauf 1",
            date=date(
                year=2023,
                month=12,
                day=29,
            ),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        EventType(
            id=2,
            name="ABC Event",
            date=date(
                year=2023,
                month=7,
                day=19,
            ),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        EventType(
            id=99,
            name="Test-Lauf 2",
            date=date(
                year=2023,
                month=12,
                day=29,
            ),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
    ]


TABLE_ID = "evnt.table"


def test_events_list_is_empty():
    html = etree.HTML(render.events_table(events=[]))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_events_list_is_not_empty(events: List[EventType]):
    html = etree.HTML(render.events_table(events=events))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Events\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "3"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Test-Lauf 1",
        "2023-12-29",
        None,
        "no",
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "2"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "ABC Event",
        "2023-07-19",
        None,
        "no",
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["id"] == "99"
    assert [td.text for td in rows[3].findall(".//td")] == [
        "Test-Lauf 2",
        "2023-12-29",
        None,
        "no",
        None,
        None,
        None,
    ]


def test_key_is_defined(events: List[EventType]):
    events[0].key = "sevenOr"
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "***"


def test_publish_is_true(events: List[EventType]):
    events[0].publish = True
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "yes"


@pytest.mark.parametrize(
    "streaming_address, streaming_key, streaming_enabled, value",
    [
        (None, None, None, None),
        ("", None, None, None),
        ("localhost:8081", None, None, None),
        (None, "", None, None),
        ("", "", None, None),
        ("localhost:8081", "", None, None),
        (None, "abcde", None, None),
        ("", "abcde", None, None),
        ("localhost:8081", "abcde", None, None),
        (None, None, False, "disabled"),
        ("", None, False, "disabled"),
        ("localhost:8081", None, False, "disabled"),
        (None, "", False, "disabled"),
        ("", "", False, "disabled"),
        ("localhost:8081", "", False, "disabled"),
        (None, "abcde", False, "disabled"),
        ("", "abcde", False, "disabled"),
        ("localhost:8081", "abcde", False, "disabled"),
        (None, None, True, "enabled"),
        ("", None, True, "enabled"),
        ("localhost:8081", None, True, "enabled"),
        (None, "", True, "enabled"),
        ("", "", True, "enabled"),
        ("localhost:8081", "", True, "enabled"),
        (None, "abcde", True, "enabled"),
        ("", "abcde", True, "enabled"),
        ("localhost:8081", "abcde", True, "enabled"),
    ],
)
def test_streaming_is_defined(
    events: List[EventType],
    streaming_address: Optional[str],
    streaming_key: Optional[str],
    streaming_enabled: bool,
    value: Optional[str],
):
    events[0].streaming_address = streaming_address
    events[0].streaming_key = streaming_key
    events[0].streaming_enabled = streaming_enabled
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == value


def test_series_is_defined(events: List[EventType]):
    events[0].series = "Run 1"
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "Run 1"


def test_one_field(events: List[EventType]):
    events[0].fields = ["Start number"]
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "Start number"


def test_two_fields(events: List[EventType]):
    events[0].fields = ["Start number", "Region"]
    html = etree.HTML(render.events_table(events=events))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "Start number, Region"

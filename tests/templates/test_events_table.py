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


import pathlib
from datetime import date
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.event_type import EventType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


def headers(table: etree.Element) -> List[str]:
    headers = []
    for h in table.findall(path=".//thead//tr//th"):
        headers.append(h.text)
    return headers


def rows(table: etree.Element) -> List[List[str]]:
    rows = []
    for row in table.findall(path=".//tbody//tr"):
        content = []
        for cell in row.findall(path=".//td"):
            content.append(cell.text)
        rows.append(content)
    return rows


def test_events_table_with_no_event(render):
    events = []
    html = etree.HTML(str(render.events_table(events=events)))

    table = html.find(".//table[@id='evnt.table']")
    assert headers(table) == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]
    assert rows(table) == []


def test_events_table_with_several_events(render):
    events = [
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
            fields=["a, b"],
            streaming_address=None,
            streaming_key=None,
            streaming_enabled=None,
        ),
        EventType(
            id=2,
            name="ABC Event",
            date=date(
                year=2023,
                month=7,
                day=19,
            ),
            key="sevenOr",
            publish=True,
            series="Run 1",
            fields=["Start number", "Region"],
            streaming_address="localhost:8081",
            streaming_key="abcde",
            streaming_enabled=True,
        ),
        EventType(
            id=99,
            name="Test-Lauf 2",
            date=date(
                year=2023,
                month=12,
                day=29,
            ),
            key="local",
            publish=False,
            series="Serie",
            fields=["e", "f"],
            streaming_address="myhost:8081",
            streaming_key="secret-key",
            streaming_enabled=False,
        ),
    ]
    html = etree.HTML(str(render.events_table(events=events)))

    table = html.find(".//table[@id='evnt.table']")
    assert headers(table) == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]
    assert rows(table) == [
        [
            "Test-Lauf 1",
            "2023-12-29",
            None,
            "no",
            None,
            None,
            "a, b",
        ],
        [
            "ABC Event",
            "2023-07-19",
            "***",
            "yes",
            "enabled",
            "Run 1",
            "Start number, Region",
        ],
        [
            "Test-Lauf 2",
            "2023-12-29",
            "***",
            "no",
            "disabled",
            "Serie",
            "e, f",
        ],
    ]

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
import pathlib
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.event_type import EventType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


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


def headers(table: etree.Element) -> List[str]:
    headers = []
    for h in table.findall(path=".//thead//tr//th"):
        headers.append(h.text)
    return headers


def rows(table: etree.Element) -> List[List[str]]:
    rows = []
    for row in table.findall(path=".//tbody//tr"):
        content = []
        for cell in row.xpath(_path=".//th | .//td"):
            content.append(cell.text)
        rows.append(content)
    return rows


def test_courses_table_with_no_courses(render, event: EventType):
    courses = []
    html = etree.HTML(str(render.courses_table(event=event, courses=courses)))

    table = html.find(".//table[@id='cou.table']")
    assert html.find(".//td[@id='cour.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='cour.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]
    assert rows(table) == []


def test_courses_table_with_several_courses(render, event: EventType):
    courses = [
        CourseType(
            id=110,
            event_id=3,
            name="Bahn B",
            length=None,
            climb=None,
            controls=[],
        ),
        CourseType(
            id=109,
            event_id=3,
            name="Bahn A",
            length=4800,
            climb=180,
            controls=["124", "131", "121", "122"],
        ),
    ]
    html = etree.HTML(str(render.courses_table(event=event, courses=courses)))

    table = html.find(".//table[@id='cou.table']")
    assert html.find(".//td[@id='cour.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='cour.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]
    assert rows(table) == [
        [
            "Courses\xa0\xa0(2)",
        ],
        [
            "Bahn B",
            None,
            None,
            None,
        ],
        [
            "Bahn A",
            "4800",
            "180",
            "124 - 131 - 121 - 122",
        ],
    ]

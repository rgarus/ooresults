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

import pytest

from ooresults.otypes.course_type import CourseType
from ooresults.otypes.event_type import EventType
from ooresults.utils import render
from tests.templates.conftest import Html


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


@pytest.fixture()
def courses() -> list[CourseType]:
    return [
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
            length=None,
            climb=None,
            controls=[],
        ),
    ]


TABLE_ID = "cou.table"


def test_courses_list_is_empty(event: EventType) -> None:
    html = Html(text=render.courses_table(event=event, courses=[]))

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_courses_list_is_not_empty(event: EventType, courses: list[CourseType]) -> None:
    html = Html(text=render.courses_table(event=event, courses=courses))

    assert html.find(path=".//td[@id='cour.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='cour.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 3

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Courses\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "110"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Bahn B",
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "109"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Bahn A",
        None,
        None,
        None,
    ]


def test_length_is_defined(event: EventType, courses: list[CourseType]) -> None:
    courses[0].length = 5400.4
    html = Html(text=render.courses_table(event=event, courses=courses))

    elem = html.find(path=f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[2]")
    assert elem.text == "5400"


def test_climb_is_defined(event: EventType, courses: list[CourseType]) -> None:
    courses[0].climb = 159.8
    html = Html(text=render.courses_table(event=event, courses=courses))

    elem = html.find(path=f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "160"


def test_controls_are_defined(event: EventType, courses: list[CourseType]) -> None:
    courses[0].controls = ["124", "137", "123", "129"]
    html = Html(text=render.courses_table(event=event, courses=courses))

    elem = html.find(path=f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "124 - 137 - 123 - 129"

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
from datetime import timezone
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_params import VoidedLeg
from ooresults.otypes.class_type import ClassInfoType
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


def test_classes_table_with_no_classes(render, event: EventType):
    classes = []
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    table = html.find(".//table[@id='cls.table']")
    assert html.find(".//td[@id='clas.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='clas.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "Name",
        "Short name",
        "Course",
        "Voided legs",
        "Type",
        "Use start control",
        "Apply handicap",
        "Mass start",
        "Time limit",
        "Penalty controls",
        "Penalty time limit",
    ]
    assert rows(table) == []


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


def test_classes_table_with_several_classes(render, event: EventType):
    classes = [
        ClassInfoType(
            id=109,
            name="Elite",
            short_name="Elite",
            course_id=122,
            course_name="Bahn A",
            course_length=4200,
            course_climb=280,
            number_of_controls=12,
            params=ClassParams(
                otype="standard",
                using_start_control="yes",
                mass_start=None,
                time_limit=None,
                penalty_controls=None,
                penalty_overtime=None,
                apply_handicap_rule=True,
                voided_legs=[
                    VoidedLeg(control_1="121", control_2="126"),
                    VoidedLeg(control_1="122", control_2="121"),
                    VoidedLeg(control_1="130", control_2="131"),
                ],
            ),
        ),
        ClassInfoType(
            id=110,
            name="Elite F",
            short_name="Elite Women",
            course_id=122,
            course_name="Bahn A",
            course_length=4200,
            course_climb=280,
            number_of_controls=12,
            params=ClassParams(
                otype="net",
                using_start_control="if_punched",
                mass_start=S1,
                time_limit=1800,
                penalty_controls=180,
                penalty_overtime=60,
                apply_handicap_rule=False,
                voided_legs=[],
            ),
        ),
        ClassInfoType(
            id=111,
            name="Elite M",
            short_name="Elite Men",
            course_id=122,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
    ]
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    table = html.find(".//table[@id='cls.table']")
    assert html.find(".//td[@id='clas.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='clas.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "Name",
        "Short name",
        "Course",
        "Voided legs",
        "Type",
        "Use start control",
        "Apply handicap",
        "Mass start",
        "Time limit",
        "Penalty controls",
        "Penalty time limit",
    ]
    assert rows(table) == [
        [
            "Classes\xa0\xa0(3)",
        ],
        [
            "Elite",
            "Elite",
            "Bahn A",
            "121-126, 122-121, 130-131",
            "Standard",
            "Yes",
            "Yes",
            None,
            None,
            None,
            None,
        ],
        [
            "Elite F",
            "Elite Women",
            "Bahn A",
            None,
            "Net",
            "If punched",
            None,
            "12:38:59",
            "30:00",
            "180",
            "60",
        ],
        [
            "Elite M",
            "Elite Men",
            None,
            None,
            "Standard",
            "If punched",
            None,
            None,
            None,
            None,
            None,
        ],
    ]

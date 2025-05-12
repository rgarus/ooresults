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


@pytest.fixture()
def classes() -> List[ClassInfoType]:
    return [
        ClassInfoType(
            id=109,
            name="Elite",
            short_name=None,
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
        ClassInfoType(
            id=110,
            name="Elite F",
            short_name=None,
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
        ClassInfoType(
            id=111,
            name="Elite M",
            short_name=None,
            course_id=None,
            course_name=None,
            course_length=None,
            course_climb=None,
            number_of_controls=None,
            params=ClassParams(),
        ),
    ]


TABLE_ID = "cls.table"


def test_class_list_is_empty(render, event: EventType):
    html = etree.HTML(str(render.classes_table(event=event, classes=[])))

    assert html.find(".//td[@id='clas.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='clas.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
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

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


def test_class_list_is_not_empty(
    render, event: EventType, classes: List[ClassInfoType]
):
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    assert html.find(".//td[@id='clas.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='clas.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
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

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Classes\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "109"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Elite",
        None,
        None,
        None,
        "Standard",
        "If punched",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "110"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Elite F",
        None,
        None,
        None,
        "Standard",
        "If punched",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["id"] == "111"
    assert [td.text for td in rows[3].findall(".//td")] == [
        "Elite M",
        None,
        None,
        None,
        "Standard",
        "If punched",
        None,
        None,
        None,
        None,
        None,
    ]


def test_short_name_is_defined(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].short_name = "E Men"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[2]")
    assert elem.text == "E Men"


def test_course_is_defined(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].course_id = 2
    classes[0].course_name = "Bahn A"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "Bahn A"


def test_one_voided_leg(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.voided_legs = [VoidedLeg("113", "115")]
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "113-115"


def test_two_voided_legs(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.voided_legs = [VoidedLeg("113", "115"), VoidedLeg("114", "126")]
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "113-115, 114-126"


def test_otype_is_net(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.otype = "net"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == "Net"


def test_otype_is_score(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.otype = "score"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == "Score"


def test_start_control_is_yes(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.using_start_control = "yes"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "Yes"


def test_start_control_is_no(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.using_start_control = "no"
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "No"


def test_apply_handicap_role_is_true(
    render, event: EventType, classes: List[ClassInfoType]
):
    classes[0].params.apply_handicap_rule = True
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "Yes"


def test_mass_start_is_defined(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.mass_start = datetime.datetime(
        year=2023,
        month=7,
        day=19,
        hour=14,
        minute=30,
        second=0,
        tzinfo=timezone.utc,
    )
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[8]")
    assert elem.text == "14:30:00"


def test_time_limit_is_defined(render, event: EventType, classes: List[ClassInfoType]):
    classes[0].params.time_limit = 2700
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[9]")
    assert elem.text == "45:00"


def test_penalty_controls_is_defined(
    render, event: EventType, classes: List[ClassInfoType]
):
    classes[0].params.penalty_controls = 240
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[10]")
    assert elem.text == "240"


def test_penalty_overtime_is_defined(
    render, event: EventType, classes: List[ClassInfoType]
):
    classes[0].params.penalty_overtime = 180
    html = etree.HTML(str(render.classes_table(event=event, classes=classes)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[11]")
    assert elem.text == "180"

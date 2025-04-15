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
from datetime import datetime
from datetime import timezone
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_params import VoidedLeg
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.course_type import CourseType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def courses() -> List[CourseType]:
    return [
        CourseType(
            id=3,
            event_id=1,
            name="Bahn A",
            length=None,
            climb=None,
            controls=["121"],
        ),
        CourseType(
            id=2,
            event_id=1,
            name="Bahn B",
            length=None,
            climb=None,
            controls=["121"],
        ),
    ]


@pytest.fixture()
def class_() -> ClassType:
    return ClassType(
        id=7,
        event_id=1,
        name="Elite Men",
        short_name=None,
        course_id=None,
        params=ClassParams(),
    )


def test_class_is_none(render, courses):
    html = etree.HTML(str(render.add_class(class_=None, courses=courses)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_short_name = html.find(".//input[@name='short_name']")
    assert input_short_name.attrib["value"] == ""

    options_course_id = html.findall(".//select[@name='course_id']/option")
    assert len(options_course_id) == 3
    assert options_course_id[0].attrib == {"value": "", "selected": "selected"}
    assert options_course_id[0].text is None
    assert options_course_id[1].attrib == {"value": "3"}
    assert options_course_id[1].text == "Bahn A"
    assert options_course_id[2].attrib == {"value": "2"}
    assert options_course_id[2].text == "Bahn B"

    input_voided_legs = html.find(".//input[@name='voided_legs']")
    assert input_voided_legs.attrib["value"] == ""

    option_type = html.findall(".//select[@name='type']/option")
    assert len(option_type) == 3
    assert option_type[0].attrib == {"value": "standard", "selected": "selected"}
    assert option_type[0].text == "Standard"
    assert option_type[1].attrib == {"value": "net"}
    assert option_type[1].text == "Net"
    assert option_type[2].attrib == {"value": "score"}
    assert option_type[2].text == "Score"

    option_start = html.findall(".//select[@name='startControl']/option")
    assert len(option_start) == 3
    assert option_start[0].attrib == {"value": "if_punched", "selected": "selected"}
    assert option_start[0].text == "If punched"
    assert option_start[1].attrib == {"value": "no"}
    assert option_start[1].text == "No"
    assert option_start[2].attrib == {"value": "yes"}
    assert option_start[2].text == "Yes"

    option_handicap = html.findall(".//select[@name='handicap']/option")
    assert len(option_handicap) == 2
    assert option_handicap[0].attrib == {"value": "0", "selected": "selected"}
    assert option_handicap[0].text == "No"
    assert option_handicap[1].attrib == {"value": "1"}
    assert option_handicap[1].text == "Yes"

    input_mass_start = html.find(".//input[@name='massStart']")
    assert input_mass_start.attrib["value"] == ""

    input_time_limit = html.find(".//input[@name='timeLimit']")
    assert input_time_limit.attrib["value"] == ""

    input_penalty_controls = html.find(".//input[@name='penaltyControls']")
    assert input_penalty_controls.attrib["value"] == ""

    input_penalty_overtime = html.find(".//input[@name='penaltyOvertime']")
    assert input_penalty_overtime.attrib["value"] == ""


def test_class_is_not_none(render, class_: ClassType, courses: List[CourseType]):
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "Elite Men"

    input_short_name = html.find(".//input[@name='short_name']")
    assert input_short_name.attrib["value"] == ""

    options_course_id = html.findall(".//select[@name='course_id']/option")
    assert len(options_course_id) == 3
    assert options_course_id[0].attrib == {"value": "", "selected": "selected"}
    assert options_course_id[0].text is None
    assert options_course_id[1].attrib == {"value": "3"}
    assert options_course_id[1].text == "Bahn A"
    assert options_course_id[2].attrib == {"value": "2"}
    assert options_course_id[2].text == "Bahn B"

    input_voided_legs = html.find(".//input[@name='voided_legs']")
    assert input_voided_legs.attrib["value"] == ""

    option_type = html.findall(".//select[@name='type']/option")
    assert len(option_type) == 3
    assert option_type[0].attrib == {"value": "standard", "selected": "selected"}
    assert option_type[0].text == "Standard"
    assert option_type[1].attrib == {"value": "net"}
    assert option_type[1].text == "Net"
    assert option_type[2].attrib == {"value": "score"}
    assert option_type[2].text == "Score"

    option_start = html.findall(".//select[@name='startControl']/option")
    assert len(option_start) == 3
    assert option_start[0].attrib == {"value": "if_punched", "selected": "selected"}
    assert option_start[0].text == "If punched"
    assert option_start[1].attrib == {"value": "no"}
    assert option_start[1].text == "No"
    assert option_start[2].attrib == {"value": "yes"}
    assert option_start[2].text == "Yes"

    option_handicap = html.findall(".//select[@name='handicap']/option")
    assert len(option_handicap) == 2
    assert option_handicap[0].attrib == {"value": "0", "selected": "selected"}
    assert option_handicap[0].text == "No"
    assert option_handicap[1].attrib == {"value": "1"}
    assert option_handicap[1].text == "Yes"

    input_mass_start = html.find(".//input[@name='massStart']")
    assert input_mass_start.attrib["value"] == ""

    input_time_limit = html.find(".//input[@name='timeLimit']")
    assert input_time_limit.attrib["value"] == ""

    input_penalty_controls = html.find(".//input[@name='penaltyControls']")
    assert input_penalty_controls.attrib["value"] == ""

    input_penalty_overtime = html.find(".//input[@name='penaltyOvertime']")
    assert input_penalty_overtime.attrib["value"] == ""


def test_short_name_is_defined(render, class_: ClassType, courses: List[CourseType]):
    class_.short_name = "E Men"
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_short_name = html.find(".//input[@name='short_name']")
    assert input_short_name.attrib["value"] == "E Men"


def test_course_id_is_2(render, class_: ClassType, courses: List[CourseType]):
    class_.course_id = 2
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    options_course_id = html.findall(".//select[@name='course_id']/option")
    assert len(options_course_id) == 3
    assert options_course_id[0].attrib == {"value": ""}
    assert options_course_id[0].text is None
    assert options_course_id[1].attrib == {"value": "3"}
    assert options_course_id[1].text == "Bahn A"
    assert options_course_id[2].attrib == {"value": "2", "selected": "selected"}
    assert options_course_id[2].text == "Bahn B"


def test_course_id_is_3(render, class_: ClassType, courses: List[CourseType]):
    class_.course_id = 3
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    options_course_id = html.findall(".//select[@name='course_id']/option")
    assert len(options_course_id) == 3
    assert options_course_id[0].attrib == {"value": ""}
    assert options_course_id[0].text is None
    assert options_course_id[1].attrib == {"value": "3", "selected": "selected"}
    assert options_course_id[1].text == "Bahn A"
    assert options_course_id[2].attrib == {"value": "2"}
    assert options_course_id[2].text == "Bahn B"


def test_otype_is_net(render, class_: ClassType, courses: List[CourseType]):
    class_.params.otype = "net"
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    option_type = html.findall(".//select[@name='type']/option")
    assert len(option_type) == 3
    assert option_type[0].attrib == {"value": "standard"}
    assert option_type[0].text == "Standard"
    assert option_type[1].attrib == {"value": "net", "selected": "selected"}
    assert option_type[1].text == "Net"
    assert option_type[2].attrib == {"value": "score"}
    assert option_type[2].text == "Score"


def test_otype_is_score(render, class_: ClassType, courses: List[CourseType]):
    class_.params.otype = "score"
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    option_type = html.findall(".//select[@name='type']/option")
    assert len(option_type) == 3
    assert option_type[0].attrib == {"value": "standard"}
    assert option_type[0].text == "Standard"
    assert option_type[1].attrib == {"value": "net"}
    assert option_type[1].text == "Net"
    assert option_type[2].attrib == {"value": "score", "selected": "selected"}
    assert option_type[2].text == "Score"


def test_start_control_is_yes(render, class_: ClassType, courses: List[CourseType]):
    class_.params.using_start_control = "yes"
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    option_start = html.findall(".//select[@name='startControl']/option")
    assert len(option_start) == 3
    assert option_start[0].attrib == {"value": "if_punched"}
    assert option_start[0].text == "If punched"
    assert option_start[1].attrib == {"value": "no"}
    assert option_start[1].text == "No"
    assert option_start[2].attrib == {"value": "yes", "selected": "selected"}
    assert option_start[2].text == "Yes"


def test_start_control_is_no(render, class_: ClassType, courses: List[CourseType]):
    class_.params.using_start_control = "no"
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    option_start = html.findall(".//select[@name='startControl']/option")
    assert len(option_start) == 3
    assert option_start[0].attrib == {"value": "if_punched"}
    assert option_start[0].text == "If punched"
    assert option_start[1].attrib == {"value": "no", "selected": "selected"}
    assert option_start[1].text == "No"
    assert option_start[2].attrib == {"value": "yes"}
    assert option_start[2].text == "Yes"


def test_mass_start_is_defined(render, class_: ClassType, courses: List[CourseType]):
    class_.params.mass_start = datetime(
        year=2023,
        month=7,
        day=19,
        hour=14,
        minute=30,
        second=0,
        tzinfo=timezone.utc,
    )
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_mass_start = html.find(".//input[@name='massStart']")
    assert input_mass_start.attrib["value"] == "14:30:00"


def test_time_limit_is_defined(render, class_: ClassType, courses: List[CourseType]):
    class_.params.time_limit = 2700
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_time_limit = html.find(".//input[@name='timeLimit']")
    assert input_time_limit.attrib["value"] == "45:00"


def test_penalty_controls_is_defined(
    render, class_: ClassType, courses: List[CourseType]
):
    class_.params.penalty_controls = 240
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_penalty_controls = html.find(".//input[@name='penaltyControls']")
    assert input_penalty_controls.attrib["value"] == "240"


def test_penalty_overtime_is_defined(
    render, class_: ClassType, courses: List[CourseType]
):
    class_.params.penalty_overtime = 180
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_penalty_overtime = html.find(".//input[@name='penaltyOvertime']")
    assert input_penalty_overtime.attrib["value"] == "180"


def test_apply_handicap_role_is_true(
    render, class_: ClassType, courses: List[CourseType]
):
    class_.params.apply_handicap_rule = True
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    option_handicap = html.findall(".//select[@name='handicap']/option")
    assert len(option_handicap) == 2
    assert option_handicap[0].attrib == {"value": "0"}
    assert option_handicap[0].text == "No"
    assert option_handicap[1].attrib == {"value": "1", "selected": "selected"}
    assert option_handicap[1].text == "Yes"


def test_one_voided_leg(render, class_: ClassType, courses: List[CourseType]):
    class_.params.voided_legs = [VoidedLeg("113", "115")]
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_voided_legs = html.find(".//input[@name='voided_legs']")
    assert input_voided_legs.attrib["value"] == "113-115"


def test_two_voided_legs(render, class_: ClassType, courses: List[CourseType]):
    class_.params.voided_legs = [VoidedLeg("113", "115"), VoidedLeg("114", "126")]
    html = etree.HTML(str(render.add_class(class_=class_, courses=courses)))

    input_voided_legs = html.find(".//input[@name='voided_legs']")
    assert input_voided_legs.attrib["value"] == "113-115, 114-126"

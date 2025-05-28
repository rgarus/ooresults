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


import pytest
from lxml import etree

from ooresults.otypes.course_type import CourseType
from ooresults.utils import render


@pytest.fixture()
def course() -> CourseType:
    return CourseType(
        id=7,
        event_id=2,
        name="Bahn A",
        length=None,
        climb=None,
        controls=[],
    )


def test_course_is_none():
    html = etree.HTML(render.add_course(course=None))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_name = html.find(".//input[@name='length']")
    assert input_name.attrib["value"] == ""

    input_name = html.find(".//input[@name='climb']")
    assert input_name.attrib["value"] == ""

    input_name = html.find(".//input[@name='controls']")
    assert input_name.attrib["value"] == ""


def test_course_is_not_none(course: CourseType):
    html = etree.HTML(render.add_course(course=course))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "Bahn A"

    input_name = html.find(".//input[@name='length']")
    assert input_name.attrib["value"] == ""

    input_name = html.find(".//input[@name='climb']")
    assert input_name.attrib["value"] == ""

    input_name = html.find(".//input[@name='controls']")
    assert input_name.attrib["value"] == ""


def test_length_is_defined(course: CourseType):
    course.length = 5400.4
    html = etree.HTML(render.add_course(course=course))

    input_name = html.find(".//input[@name='length']")
    assert input_name.attrib["value"] == "5400"


def test_climb_is_defined(course: CourseType):
    course.climb = 159.8
    html = etree.HTML(render.add_course(course=course))

    input_name = html.find(".//input[@name='climb']")
    assert input_name.attrib["value"] == "160"


def test_controls_are_defined(course: CourseType):
    course.controls = ["124", "137", "123", "129"]
    html = etree.HTML(render.add_course(course=course))

    input_name = html.find(".//input[@name='controls']")
    assert input_name.attrib["value"] == "124 - 137 - 123 - 129"

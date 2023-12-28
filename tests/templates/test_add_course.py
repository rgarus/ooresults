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

import pytest
import web
from lxml import etree

import ooresults
from ooresults.repo.course_type import CourseType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


def test_add_course_for_add(render):
    course = None
    html = etree.HTML(str(render.add_course(course)))

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


def test_add_course_for_edit(render):
    course = CourseType(
        id=7,
        event_id=2,
        name="Bahn A",
        length=5400,
        climb=160,
        controls=["124", "137", "123", "129"],
    )
    html = etree.HTML(str(render.add_course(course)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "Bahn A"

    input_name = html.find(".//input[@name='length']")
    assert input_name.attrib["value"] == "5400"

    input_name = html.find(".//input[@name='climb']")
    assert input_name.attrib["value"] == "160"

    input_name = html.find(".//input[@name='controls']")
    assert input_name.attrib["value"] == "124 - 137 - 123 - 129"

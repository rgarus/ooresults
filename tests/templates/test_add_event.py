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

import pytest
import web
from lxml import etree

import ooresults
from ooresults.repo.event_type import EventType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


def test_add_event_for_add(render):
    event = None
    html = etree.HTML(str(render.add_event(event)))

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_date = html.find(".//input[@name='date']")
    assert input_date.attrib["value"] == ""

    input_key = html.find(".//input[@name='key']")
    assert input_key.attrib["value"] == ""

    options_publish = html.findall(".//select[@name='publish']/option")
    assert len(options_publish) == 2
    assert options_publish[0].attrib == {"value": "no", "selected": "selected"}
    assert options_publish[0].text == "no"
    assert options_publish[1].attrib == {"value": "yes"}
    assert options_publish[1].text == "yes"

    input_series = html.find(".//input[@name='series']")
    assert input_series.attrib["value"] == ""

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == ""


def test_add_event_for_edit(render):
    event = EventType(
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
    )
    html = etree.HTML(str(render.add_event(event)))

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "ABC Event"

    input_date = html.find(".//input[@name='date']")
    assert input_date.attrib["value"] == "2023-07-19"

    input_key = html.find(".//input[@name='key']")
    assert input_key.attrib["value"] == "sevenOr"

    options_publish = html.findall(".//select[@name='publish']/option")
    assert len(options_publish) == 2
    assert options_publish[0].attrib == {"value": "no"}
    assert options_publish[0].text == "no"
    assert options_publish[1].attrib == {"value": "yes", "selected": "selected"}
    assert options_publish[1].text == "yes"

    input_series = html.find(".//input[@name='series']")
    assert input_series.attrib["value"] == "Run 1"

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == "Start number, Region"

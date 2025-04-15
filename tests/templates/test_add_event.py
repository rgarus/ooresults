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
from ooresults.otypes.event_type import EventType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def event() -> EventType:
    return EventType(
        id=2,
        name="ABC Event",
        date=date(year=2023, month=7, day=19),
        key=None,
        publish=False,
        series=None,
        fields=[],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )


def test_event_is_none(render):
    html = etree.HTML(str(render.add_event(event=None)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_date = html.find(".//input[@name='date']")
    assert input_date.attrib["value"] == ""

    input_key = html.find(".//input[@name='key']")
    assert input_key.attrib["value"] == ""

    input_publish = html.find(".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" not in input_publish.attrib

    input_streaming_address = html.find(".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == ""

    input_streaming_key = html.find(".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == ""

    input_streaming_enabled = html.find(".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib

    input_series = html.find(".//input[@name='series']")
    assert input_series.attrib["value"] == ""

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == ""


def test_event_is_not_none(render, event: EventType):
    html = etree.HTML(str(render.add_event(event=event)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "2"

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "ABC Event"

    input_date = html.find(".//input[@name='date']")
    assert input_date.attrib["value"] == "2023-07-19"

    input_key = html.find(".//input[@name='key']")
    assert input_key.attrib["value"] == ""

    input_publish = html.find(".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" not in input_publish.attrib

    input_streaming_address = html.find(".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == ""

    input_streaming_key = html.find(".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == ""

    input_streaming_enabled = html.find(".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib

    input_series = html.find(".//input[@name='series']")
    assert input_series.attrib["value"] == ""

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == ""


def test_key_is_defined(render, event: EventType):
    event.key = "sevenOr"
    html = etree.HTML(str(render.add_event(event=event)))

    input_key = html.find(".//input[@name='key']")
    assert input_key.attrib["value"] == "sevenOr"


def test_publish_is_true(render, event: EventType):
    event.publish = True
    html = etree.HTML(str(render.add_event(event=event)))

    input_publish = html.find(".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" in input_publish.attrib


def test_series_is_defined(render, event: EventType):
    event.series = "Run 1"
    html = etree.HTML(str(render.add_event(event=event)))

    input_series = html.find(".//input[@name='series']")
    assert input_series.attrib["value"] == "Run 1"


def test_one_field(render, event: EventType):
    event.fields = ["Start number"]
    html = etree.HTML(str(render.add_event(event=event)))

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == "Start number"


def test_two_fields(render, event: EventType):
    event.fields = ["Start number", "Region"]
    html = etree.HTML(str(render.add_event(event=event)))

    input_fields = html.find(".//input[@name='fields']")
    assert input_fields.attrib["value"] == "Start number, Region"


def test_streaming_address_is_defined(render, event: EventType):
    event.streaming_address = "localhost:8081"
    html = etree.HTML(str(render.add_event(event=event)))

    input_streaming_address = html.find(".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == "localhost:8081"


def test_streaming_key_is_defined(render, event: EventType):
    event.streaming_key = "abcde"
    html = etree.HTML(str(render.add_event(event=event)))

    input_streaming_key = html.find(".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == "abcde"


def test_streaming_enabled_is_false(render, event: EventType):
    event.streaming_enabled = False
    html = etree.HTML(str(render.add_event(event=event)))

    input_streaming_enabled = html.find(".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib


def test_streaming_enabled_is_true(render, event: EventType):
    event.streaming_enabled = True
    html = etree.HTML(str(render.add_event(event=event)))

    input_streaming_enabled = html.find(".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" in input_streaming_enabled.attrib

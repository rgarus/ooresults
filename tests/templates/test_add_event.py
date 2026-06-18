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


from datetime import date

import pytest

from ooresults.otypes.event_type import EventType
from ooresults.utils import render
from tests.templates.conftest import Html


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


def test_event_is_none() -> None:
    html = Html(text=render.add_event(event=None))

    input_id = html.find(path=".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_name = html.find(path=".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_date = html.find(path=".//input[@name='date']")
    assert input_date.attrib["value"] == ""

    input_key = html.find(path=".//input[@name='key']")
    assert input_key.attrib["value"] == ""

    input_publish = html.find(path=".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" not in input_publish.attrib

    input_streaming_address = html.find(path=".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == ""

    input_streaming_key = html.find(path=".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == ""

    input_streaming_enabled = html.find(path=".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib

    input_series = html.find(path=".//input[@name='series']")
    assert input_series.attrib["value"] == ""

    input_fields = html.find(path=".//input[@name='fields']")
    assert input_fields.attrib["value"] == ""


def test_event_is_not_none(event: EventType) -> None:
    html = Html(text=render.add_event(event=event))

    input_id = html.find(path=".//input[@name='id']")
    assert input_id.attrib["value"] == "2"

    input_name = html.find(path=".//input[@name='name']")
    assert input_name.attrib["value"] == "ABC Event"

    input_date = html.find(path=".//input[@name='date']")
    assert input_date.attrib["value"] == "2023-07-19"

    input_key = html.find(path=".//input[@name='key']")
    assert input_key.attrib["value"] == ""

    input_publish = html.find(path=".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" not in input_publish.attrib

    input_streaming_address = html.find(path=".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == ""

    input_streaming_key = html.find(path=".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == ""

    input_streaming_enabled = html.find(path=".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib

    input_series = html.find(path=".//input[@name='series']")
    assert input_series.attrib["value"] == ""

    input_fields = html.find(path=".//input[@name='fields']")
    assert input_fields.attrib["value"] == ""


def test_key_is_defined(event: EventType) -> None:
    event.key = "sevenOr"
    html = Html(text=render.add_event(event=event))

    input_key = html.find(path=".//input[@name='key']")
    assert input_key.attrib["value"] == "sevenOr"


def test_publish_is_true(event: EventType) -> None:
    event.publish = True
    html = Html(text=render.add_event(event=event))

    input_publish = html.find(path=".//input[@name='publish']")
    assert input_publish.attrib["value"] == "true"
    assert "checked" in input_publish.attrib


def test_series_is_defined(event: EventType) -> None:
    event.series = "Run 1"
    html = Html(text=render.add_event(event=event))

    input_series = html.find(path=".//input[@name='series']")
    assert input_series.attrib["value"] == "Run 1"


def test_one_field(event: EventType) -> None:
    event.fields = ["Start number"]
    html = Html(text=render.add_event(event=event))

    input_fields = html.find(path=".//input[@name='fields']")
    assert input_fields.attrib["value"] == "Start number"


def test_two_fields(event: EventType) -> None:
    event.fields = ["Start number", "Region"]
    html = Html(text=render.add_event(event=event))

    input_fields = html.find(path=".//input[@name='fields']")
    assert input_fields.attrib["value"] == "Start number, Region"


def test_streaming_address_is_defined(event: EventType) -> None:
    event.streaming_address = "localhost:8081"
    html = Html(text=render.add_event(event=event))

    input_streaming_address = html.find(path=".//input[@name='streaming_address']")
    assert input_streaming_address.attrib["value"] == "localhost:8081"


def test_streaming_key_is_defined(event: EventType) -> None:
    event.streaming_key = "abcde"
    html = Html(text=render.add_event(event=event))

    input_streaming_key = html.find(path=".//input[@name='streaming_key']")
    assert input_streaming_key.attrib["value"] == "abcde"


def test_streaming_enabled_is_false(event: EventType) -> None:
    event.streaming_enabled = False
    html = Html(text=render.add_event(event=event))

    input_streaming_enabled = html.find(path=".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" not in input_streaming_enabled.attrib


def test_streaming_enabled_is_true(event: EventType) -> None:
    event.streaming_enabled = True
    html = Html(text=render.add_event(event=event))

    input_streaming_enabled = html.find(path=".//input[@name='streaming_enabled']")
    assert input_streaming_enabled.attrib["value"] == "true"
    assert "checked" in input_streaming_enabled.attrib

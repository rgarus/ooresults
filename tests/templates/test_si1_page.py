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
        id=3,
        name="Test-Lauf 1",
        date=date(
            year=2023,
            month=12,
            day=29,
        ),
        key=None,
        publish=False,
        series=None,
        fields=[],
    )


def test_event_is_none() -> None:
    html = Html(text=render.si1_page(event=None, view=0))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert "var eventId = null;" in script
    assert 'var eventName = "";' in script
    assert 'var eventDate = "";' in script


def test_event_is_not_none(event: EventType) -> None:
    html = Html(text=render.si1_page(event=event, view=0))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert f"var eventId = {event.id};" in script
    assert f'var eventName = "{event.name}";' in script
    assert f'var eventDate = "{event.date.isoformat()}";' in script


@pytest.mark.parametrize(
    "view, value",
    [
        (0, "0"),
        (1, "1"),
    ],
)
def test_view(event: EventType, view: int, value: str) -> None:
    html = Html(text=render.si1_page(event=event, view=view))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert f"var view = {value};  // 0: both, 1: only reader" in script

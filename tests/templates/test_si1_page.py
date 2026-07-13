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


from typing import Optional

import pytest

from ooresults.utils import render
from tests.templates.conftest import Html


@pytest.mark.parametrize(
    "event_id, value",
    [
        (None, ""),
        (2, "2"),
    ],
)
def test_event_id(event_id: Optional[int], value: str) -> None:
    html = Html(text=render.si1_page(event_id=event_id, key=None, view=0))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert f'var event_id = "{value}";' in script


@pytest.mark.parametrize(
    "key, value",
    [
        (None, ""),
        ("", ""),
        ("abc", "abc"),
        ("<&>", "<&>"),
    ],
)
def test_key(key: Optional[str], value: str) -> None:
    html = Html(text=render.si1_page(event_id=None, key=key, view=0))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert f'var key = "{value}";' in script


@pytest.mark.parametrize(
    "view, value",
    [
        (0, "0"),
        (1, "1"),
    ],
)
def test_view(view: int, value: str) -> None:
    html = Html(text=render.si1_page(event_id=None, key=None, view=view))

    elem = html.find(path="body/script")
    assert elem is not None and elem.text is not None
    script = [line.strip() for line in elem.text.splitlines()]
    assert f"var view = {value};  // 0: both, 1: only reader" in script

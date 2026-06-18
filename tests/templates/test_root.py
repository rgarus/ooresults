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


from ooresults.utils import render
from tests.templates.conftest import Html


def test_results_table_is_none() -> None:
    html = Html(text=render.root(results_table=None))

    elem = html.find(path="body/h2")
    assert elem.text == "No results available"


def test_results_table_is_not_none() -> None:
    html = Html(text=render.root(results_table="<p>abc</p>"))

    elem = html.find(path="body/p")
    assert elem.text == "abc"

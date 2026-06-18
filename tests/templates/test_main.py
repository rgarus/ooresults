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


def test_events_list_is_empty() -> None:
    html = Html(text=render.main(events=[]))

    assert len(html.findall(path=".//div[@id='tabs']")) == 1
    assert len(html.findall(path=".//div[@id='eve_actions']")) == 1
    assert len(html.findall(path=".//div[@id='entr.actions']")) == 1
    assert len(html.findall(path=".//div[@id='clas.actions']")) == 1
    assert len(html.findall(path=".//div[@id='cour.actions']")) == 1
    assert len(html.findall(path=".//div[@id='comp.actions']")) == 1
    assert len(html.findall(path=".//div[@id='club.actions']")) == 1

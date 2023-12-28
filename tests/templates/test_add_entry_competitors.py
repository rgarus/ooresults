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
from ooresults.repo.competitor_type import CompetitorType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


def test_add_entry_competitors(render):
    competitors = [
        CompetitorType(
            id=7,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            chip="1234567",
            club_id=2,
            club_name="OL Bundestag",
        ),
        CompetitorType(
            id=17,
            first_name="Birgit",
            last_name="Merkel",
            gender="F",
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
    ]
    html = etree.HTML(str(render.add_entry_competitors(competitors)))

    trs = html.findall(".//tbody/tr")
    assert len(trs) == 2

    assert html.find(".//tbody/tr[1]").attrib["id"] == "7"
    assert html.find(".//tbody/tr[1]/td[1]").text == "Angela"
    assert html.find(".//tbody/tr[1]/td[2]").text == "Merkel"
    assert html.find(".//tbody/tr[1]/td[3]").text == "F"
    assert html.find(".//tbody/tr[1]/td[4]").text == "1957"
    assert html.find(".//tbody/tr[1]/td[5]").text == "1234567"
    assert html.find(".//tbody/tr[1]/td[6]").text == "OL Bundestag"
    assert html.find(".//tbody/tr[1]/td[7]").text == "2"

    assert html.find(".//tbody/tr[2]").attrib["id"] == "17"
    assert html.find(".//tbody/tr[2]/td[1]").text == "Birgit"
    assert html.find(".//tbody/tr[2]/td[2]").text == "Merkel"
    assert html.find(".//tbody/tr[2]/td[3]").text == "F"
    assert html.find(".//tbody/tr[2]/td[4]").text is None
    assert html.find(".//tbody/tr[2]/td[5]").text is None
    assert html.find(".//tbody/tr[2]/td[6]").text is None
    assert html.find(".//tbody/tr[2]/td[7]").text is None

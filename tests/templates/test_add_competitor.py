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
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.repo.club_type import ClubType
from ooresults.repo.competitor_type import CompetitorType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def clubs() -> List[ClubType]:
    return [ClubType(id=3, name="OC Bundestag"), ClubType(id=2, name="OL Bundestag")]


def test_add_competitor_for_add(render, clubs):
    competitor = None
    html = etree.HTML(str(render.add_competitor(competitor, clubs)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == ""

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == ""

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": "", "selected": "selected"}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == ""

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == ""

    option_club = html.findall(".//select[@name='club_id']/option")
    assert len(option_club) == 3
    assert option_club[0].attrib == {"value": "", "selected": "selected"}
    assert option_club[0].text is None
    assert option_club[1].attrib == {"value": "3"}
    assert option_club[1].text == "OC Bundestag"
    assert option_club[2].attrib == {"value": "2"}
    assert option_club[2].text == "OL Bundestag"


def test_add_competitor_for_edit(render, clubs):
    competitor = CompetitorType(
        id=7,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="1234567",
        club_id=2,
        club_name="OL Bundestag",
    )
    html = etree.HTML(str(render.add_competitor(competitor, clubs)))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == "Angela"

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == "Merkel"

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F", "selected": "selected"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == "1957"

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == "1234567"

    option_club = html.findall(".//select[@name='club_id']/option")
    assert len(option_club) == 3
    assert option_club[0].attrib == {"value": ""}
    assert option_club[0].text is None
    assert option_club[1].attrib == {"value": "3"}
    assert option_club[1].text == "OC Bundestag"
    assert option_club[2].attrib == {"value": "2", "selected": "selected"}
    assert option_club[2].text == "OL Bundestag"

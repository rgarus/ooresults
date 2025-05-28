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


from typing import List

import pytest
from lxml import etree

from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.utils import render


@pytest.fixture()
def clubs() -> List[ClubType]:
    return [ClubType(id=3, name="OC Bundestag"), ClubType(id=2, name="OL Bundestag")]


@pytest.fixture()
def competitor() -> CompetitorType:
    return CompetitorType(
        id=7,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        chip=None,
        club_id=None,
        club_name=None,
    )


def test_competitor_is_none(clubs: List[ClubType]):
    html = etree.HTML(render.add_competitor(competitor=None, clubs=clubs))

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


def test_competitor_is_not_none(competitor: CompetitorType, clubs: List[ClubType]):
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == "Angela"

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == "Merkel"

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


def test_gender_is_unknown(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.gender = ""
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": "", "selected": "selected"}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"


def test_gender_is_female(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.gender = "F"
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F", "selected": "selected"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"


def test_gender_is_male(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.gender = "M"
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M", "selected": "selected"}
    assert options_gender[2].text == "M"


def test_year_is_defined(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.year = 1957
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == "1957"


def test_chip_is_defined(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.chip = "1234567"
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    input_year = html.find(".//input[@name='chip']")
    assert input_year.attrib["value"] == "1234567"


def test_club_id_is_2(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.club_id = 2
    competitor.club_name = "OL Bundestag"
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    option_club = html.findall(".//select[@name='club_id']/option")
    assert len(option_club) == 3
    assert option_club[0].attrib == {"value": ""}
    assert option_club[0].text is None
    assert option_club[1].attrib == {"value": "3"}
    assert option_club[1].text == "OC Bundestag"
    assert option_club[2].attrib == {"value": "2", "selected": "selected"}
    assert option_club[2].text == "OL Bundestag"


def test_club_id_is_3(competitor: CompetitorType, clubs: List[ClubType]):
    competitor.club_id = 3
    competitor.club_name = "OC Bundestag"
    html = etree.HTML(render.add_competitor(competitor=competitor, clubs=clubs))

    option_club = html.findall(".//select[@name='club_id']/option")
    assert len(option_club) == 3
    assert option_club[0].attrib == {"value": ""}
    assert option_club[0].text is None
    assert option_club[1].attrib == {"value": "3", "selected": "selected"}
    assert option_club[1].text == "OC Bundestag"
    assert option_club[2].attrib == {"value": "2"}
    assert option_club[2].text == "OL Bundestag"

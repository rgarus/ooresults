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


import pytest

from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.competitor_type import Sex
from ooresults.utils import render
from tests.templates.conftest import Html


@pytest.fixture()
def competitor() -> CompetitorType:
    return CompetitorType(
        id=7,
        first_name="Annalena",
        last_name="Baerbock",
        sex=Sex.FEMALE,
        year=1980,
        chip="7379879",
        club_id=3,
        club_name="OC Grün",
    )


def test_competitor_is_none() -> None:
    html = Html(text=render.merge_competitors(competitor=None))

    element = html.find(path=".//input[@name='id1']")
    assert "value" not in element.attrib or element.attrib["value"] == ""
    element = html.find(path=".//input[@name='id2']")
    assert "value" not in element.attrib or element.attrib["value"] == ""

    element = html.find(path=".//button[@id='comp.merge.choose_1']")
    assert element.text == "Choose ..."
    element = html.find(path=".//button[@id='comp.merge.choose_2']")
    assert element.text == "Choose ..."

    element = html.find(path=".//td[@id='comp.merge.firstName1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.firstName2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.lastName1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.lastName2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.sex1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.sex2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.year1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.year2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.chip1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.chip2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.club1']")
    assert element.text is None
    element = html.find(path=".//td[@id='comp.merge.club2']")
    assert element.text is None

    element = html.find(path=".//button[@id='comp.merge.1to2']")
    assert element.text == "Merge 1 --> 2"
    element = html.find(path=".//button[@id='comp.merge.2to1']")
    assert element.text == "Merge 2 --> 1"


def test_competitor_is_not_none(competitor: CompetitorType) -> None:
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//input[@name='id1']")
    assert element.attrib["value"] == "7"
    element = html.find(path=".//input[@name='id2']")
    assert "value" not in element.attrib or element.attrib["value"] == ""

    element = html.find(path=".//button[@id='comp.merge.choose_1']")
    assert element.text == "Choose ..."
    element = html.find(path=".//button[@id='comp.merge.choose_2']")
    assert element.text == "Choose ..."

    element = html.find(path=".//td[@id='comp.merge.firstName1']")
    assert element.text == "Annalena"
    element = html.find(path=".//td[@id='comp.merge.firstName2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.lastName1']")
    assert element.text == "Baerbock"
    element = html.find(path=".//td[@id='comp.merge.lastName2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.sex1']")
    assert element.text == "F"
    element = html.find(path=".//td[@id='comp.merge.sex2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.year1']")
    assert element.text == "1980"
    element = html.find(path=".//td[@id='comp.merge.year2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.chip1']")
    assert element.text == "7379879"
    element = html.find(path=".//td[@id='comp.merge.chip2']")
    assert element.text is None

    element = html.find(path=".//td[@id='comp.merge.club1']")
    assert element.text == "OC Grün"
    element = html.find(path=".//td[@id='comp.merge.club2']")
    assert element.text is None

    element = html.find(path=".//button[@id='comp.merge.1to2']")
    assert element.text == "Merge 1 --> 2"
    element = html.find(path=".//button[@id='comp.merge.2to1']")
    assert element.text == "Merge 2 --> 1"


def test_sex_is_unknown(competitor: CompetitorType) -> None:
    competitor.sex = None
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.sex1']")
    assert element.text is None


def test_sex_is_female(competitor: CompetitorType) -> None:
    competitor.sex = Sex.FEMALE
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.sex1']")
    assert element.text == "F"


def test_sex_is_male(competitor: CompetitorType) -> None:
    competitor.sex = Sex.MALE
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.sex1']")
    assert element.text == "M"


def test_year_is_undefined(competitor: CompetitorType) -> None:
    competitor.year = None
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.year1']")
    assert element.text is None


def test_chip_is_undefined(competitor: CompetitorType) -> None:
    competitor.chip = None
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.chip1']")
    assert element.text is None


def test_club_is_undefined(competitor: CompetitorType) -> None:
    competitor.club_name = None
    html = Html(text=render.merge_competitors(competitor=competitor))

    element = html.find(path=".//td[@id='comp.merge.club1']")
    assert element.text is None

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
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def competitors() -> List[CompetitorType]:
    return [
        CompetitorType(
            id=112,
            first_name="Barbara",
            last_name="Merkel",
            gender=None,
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
        CompetitorType(
            id=113,
            first_name="Angela",
            last_name="Merkel",
            gender=None,
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
        CompetitorType(
            id=114,
            first_name="Manfred",
            last_name="Merkel",
            gender=None,
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
    ]


TABLE_ID = "comp.table"


def test_competitor_list_is_empty(render):
    html = etree.HTML(str(render.competitors_table(competitors=[])))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_competitor_list_is_not_empty(render, competitors: List[CompetitorType]):
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Competitors\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "112"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "113"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Angela",
        "Merkel",
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["id"] == "114"
    assert [td.text for td in rows[3].findall(".//td")] == [
        "Manfred",
        "Merkel",
        None,
        None,
        None,
        None,
    ]


def test_gender_is_unknown(render, competitors: List[CompetitorType]):
    competitors[0].gender = ""
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text is None


def test_gender_is_female(render, competitors: List[CompetitorType]):
    competitors[0].gender = "F"
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "F"


def test_gender_is_male(render, competitors: List[CompetitorType]):
    competitors[0].gender = "M"
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "M"


def test_year_is_defined(render, competitors: List[CompetitorType]):
    competitors[0].year = 1957
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "1957"


def test_chip_is_defined(render, competitors: List[CompetitorType]):
    competitors[0].chip = "1234567"
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == "1234567"


def test_club_is_defined(render, competitors: List[CompetitorType]):
    competitors[0].club_id = 2
    competitors[0].club_name = "OL Bundestag"
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "OL Bundestag"

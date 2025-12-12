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

from ooresults.otypes.competitor_type import CompetitorType
from ooresults.utils import render


@pytest.fixture()
def competitors() -> List[CompetitorType]:
    return [
        CompetitorType(
            id=7,
            first_name="Angela",
            last_name="Merkel",
            gender=None,
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
        CompetitorType(
            id=17,
            first_name="Birgit",
            last_name="Derkel",
            gender=None,
            year=None,
            chip=None,
            club_id=None,
            club_name=None,
        ),
    ]


def test_competitor_list_is_not_empty(competitors: List[CompetitorType]):
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    trs = html.findall(".//tbody/tr")
    assert len(trs) == 2

    assert html.find(".//tbody/tr[1]").attrib["data-id"] == "7"
    assert html.find(".//tbody/tr[1]/td[1]").text == "Angela"
    assert html.find(".//tbody/tr[1]/td[2]").text == "Merkel"
    assert html.find(".//tbody/tr[1]/td[3]").text is None
    assert html.find(".//tbody/tr[1]/td[4]").text is None
    assert html.find(".//tbody/tr[1]/td[5]").text is None
    assert html.find(".//tbody/tr[1]/td[6]").text is None
    assert html.find(".//tbody/tr[1]/td[7]").text is None

    assert html.find(".//tbody/tr[2]").attrib["data-id"] == "17"
    assert html.find(".//tbody/tr[2]/td[1]").text == "Birgit"
    assert html.find(".//tbody/tr[2]/td[2]").text == "Derkel"
    assert html.find(".//tbody/tr[2]/td[3]").text is None
    assert html.find(".//tbody/tr[2]/td[4]").text is None
    assert html.find(".//tbody/tr[2]/td[5]").text is None
    assert html.find(".//tbody/tr[2]/td[6]").text is None
    assert html.find(".//tbody/tr[2]/td[7]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_unknown(competitors: List[CompetitorType], row: int):
    competitors[row - 1].gender = ""
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        assert html.find(f".//tbody/tr[{i}]/td[3]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_female(competitors: List[CompetitorType], row: int):
    competitors[row - 1].gender = "F"
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            assert html.find(f".//tbody/tr[{i}]/td[3]").text == "F"
        else:
            assert html.find(f".//tbody/tr[{i}]/td[3]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_male(competitors: List[CompetitorType], row: int):
    competitors[row - 1].gender = "M"
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            assert html.find(f".//tbody/tr[{i}]/td[3]").text == "M"
        else:
            assert html.find(f".//tbody/tr[{i}]/td[3]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_year_is_defined(competitors: List[CompetitorType], row: int):
    competitors[row - 1].year = 1957
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            assert html.find(f".//tbody/tr[{i}]/td[4]").text == "1957"
        else:
            assert html.find(f".//tbody/tr[{i}]/td[4]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_chip_is_defined(competitors: List[CompetitorType], row: int):
    competitors[row - 1].chip = "1234567"
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            assert html.find(f".//tbody/tr[{i}]/td[5]").text == "1234567"
        else:
            assert html.find(f".//tbody/tr[{i}]/td[5]").text is None


@pytest.mark.parametrize("row", [1, 2])
def test_club_is_defined(competitors: List[CompetitorType], row: int):
    competitors[row - 1].club_id = 2
    competitors[row - 1].club_name = "OL Bundestag"
    html = etree.HTML(render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            assert html.find(f".//tbody/tr[{i}]/td[6]").text == "OL Bundestag"
            assert html.find(f".//tbody/tr[{i}]/td[7]").text == "2"
        else:
            assert html.find(f".//tbody/tr[{i}]/td[6]").text is None
            assert html.find(f".//tbody/tr[{i}]/td[7]").text is None

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
from lxml import etree

from ooresults.otypes.competitor_type import CompetitorType
from ooresults.utils import render


@pytest.fixture()
def competitors() -> list[CompetitorType]:
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


def test_competitor_list_is_empty():
    html = etree.HTML(render.competitors_table(competitors=[]))

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


def test_competitor_list_is_not_empty(competitors: list[CompetitorType]):
    html = etree.HTML(render.competitors_table(competitors=competitors))

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
    assert rows[1].attrib["data-id"] == "112"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "113"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Angela",
        "Merkel",
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["data-id"] == "114"
    assert [td.text for td in rows[3].findall(".//td")] == [
        "Manfred",
        "Merkel",
        None,
        None,
        None,
        None,
    ]


def test_gender_is_unknown(competitors: list[CompetitorType]):
    competitors[0].gender = ""
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text is None


def test_gender_is_female(competitors: list[CompetitorType]):
    competitors[0].gender = "F"
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "F"


def test_gender_is_male(competitors: list[CompetitorType]):
    competitors[0].gender = "M"
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "M"


def test_year_is_defined(competitors: list[CompetitorType]):
    competitors[0].year = 1957
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "1957"


def test_chip_is_defined(competitors: list[CompetitorType]):
    competitors[0].chip = "1234567"
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == "1234567"


def test_club_is_defined(competitors: list[CompetitorType]):
    competitors[0].club_id = 2
    competitors[0].club_name = "OL Bundestag"
    html = etree.HTML(render.competitors_table(competitors=competitors))

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "OL Bundestag"

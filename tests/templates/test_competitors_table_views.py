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
from ooresults.utils import render
from tests.templates.conftest import Html


TABLE_ID = "comp.table"


@pytest.fixture()
def competitor_1() -> CompetitorType:
    return CompetitorType(
        id=111,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="87121314",
        club_id=415,
        club_name="OL Bundestag",
    )


@pytest.fixture()
def competitor_2() -> CompetitorType:
    return CompetitorType(
        id=112,
        first_name="Barbara",
        last_name="Merkel",
        gender=None,
        year=None,
        chip=None,
        club_id=None,
        club_name=None,
    )


def test_competitor_list_with_view_is_competitors(
    competitor_1: CompetitorType, competitor_2: CompetitorType
) -> None:
    html = Html(
        text=render.competitors_table(
            view="competitors",
            view_comp_list=[(None, [competitor_1, competitor_2])],
        )
    )

    view = html.findall(path=".//select[@id='comp.view']/option")
    assert len(view) == 2
    assert view[0].attrib == {"value": "competitors", "selected": "selected"}
    assert view[0].text == "Competitors"
    assert view[1].attrib == {"value": "clubs"}
    assert view[1].text == "Clubs"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 3

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Competitors\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "111"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
        "OL Bundestag",
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "112"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
    ]


def test_competitor_list_with_view_is_clubs(
    competitor_1: CompetitorType, competitor_2: CompetitorType
) -> None:
    html = Html(
        text=render.competitors_table(
            view="clubs",
            view_comp_list=[(None, [competitor_2]), ("OL Bundestag", [competitor_1])],
        )
    )

    view = html.findall(path=".//select[@id='comp.view']/option")
    assert len(view) == 2
    assert view[0].attrib == {"value": "competitors"}
    assert view[0].text == "Competitors"
    assert view[1].attrib == {"value": "clubs", "selected": "selected"}
    assert view[1].text == "Clubs"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "-- Not assigned to any club --\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "112"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "Barbara",
        "Merkel",
        None,
        None,
        None,
    ]

    # row 3
    assert [th.text for th in rows[2].findall(".//th")] == [
        "OL Bundestag\xa0\xa0(1)",
    ]

    # row 4
    assert rows[3].attrib["data-id"] == "111"
    assert [td.text for td in rows[3].findall(".//td")] == [
        "Angela",
        "Merkel",
        "F",
        "1957",
        "87121314",
    ]

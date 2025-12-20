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

from ooresults.otypes.club_type import ClubType
from ooresults.utils import render


@pytest.fixture()
def clubs() -> list[ClubType]:
    return [
        ClubType(
            id=145,
            name="OL Bundestag",
        ),
        ClubType(
            id=146,
            name="Orieentering club",
        ),
    ]


TABLE_ID = "clb.table"


def test_club_list_is_empty():
    html = etree.HTML(render.clubs_table(clubs=[]))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_club_list_is_not_empty(clubs: list[ClubType]):
    html = etree.HTML(render.clubs_table(clubs=clubs))

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Name",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 3

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Clubs\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "145"
    assert [td.text for td in rows[1].findall(".//td")] == [
        "OL Bundestag",
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "146"
    assert [td.text for td in rows[2].findall(".//td")] == [
        "Orieentering club",
    ]

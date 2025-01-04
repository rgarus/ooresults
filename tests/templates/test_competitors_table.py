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


def headers(table: etree.Element) -> List[str]:
    headers = []
    for h in table.findall(path=".//thead//tr//th"):
        headers.append(h.text)
    return headers


def rows(table: etree.Element) -> List[List[str]]:
    rows = []
    for row in table.findall(path=".//tbody//tr"):
        content = []
        for cell in row.xpath(_path=".//th | .//td"):
            content.append(cell.text)
        rows.append(content)
    return rows


def test_competitors_table_with_no_competitors(render):
    competitors = []
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    table = html.find(".//table[@id='comp.table']")

    assert headers(table) == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]
    assert rows(table) == []


def test_competitors_table_with_several_competitors(render):
    competitors = [
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
            gender="F",
            year=1957,
            chip="4748495",
            club_id=145,
            club_name="OL Bundestag",
        ),
        CompetitorType(
            id=114,
            first_name="Manfred",
            last_name="Merkel",
            gender="M",
            year=1959,
            chip="4748496",
            club_id=145,
            club_name="OL Bundestag",
        ),
    ]
    html = etree.HTML(str(render.competitors_table(competitors=competitors)))

    table = html.find(".//table[@id='comp.table']")

    assert headers(table) == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]
    assert rows(table) == [
        [
            "Competitors\xa0\xa0(3)",
        ],
        [
            "Barbara",
            "Merkel",
            None,
            None,
            None,
            None,
        ],
        [
            "Angela",
            "Merkel",
            "F",
            "1957",
            "4748495",
            "OL Bundestag",
        ],
        [
            "Manfred",
            "Merkel",
            "M",
            "1959",
            "4748496",
            "OL Bundestag",
        ],
    ]

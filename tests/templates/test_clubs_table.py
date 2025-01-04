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
from ooresults.otypes.club_type import ClubType
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


def test_clubs_table_with_no_clubs(render):
    clubs = []
    html = etree.HTML(str(render.clubs_table(clubs=clubs)))

    table = html.find(".//table[@id='clb.table']")

    assert headers(table) == [
        "Name",
    ]
    assert rows(table) == []


def test_clubs_table_with_several_clubs(render):
    clubs = [
        ClubType(
            id=145,
            name="OL Bundestag",
        ),
        ClubType(
            id=146,
            name="Orieentering club",
        ),
    ]
    html = etree.HTML(str(render.clubs_table(clubs=clubs)))

    table = html.find(".//table[@id='clb.table']")

    assert headers(table) == [
        "Name",
    ]
    assert rows(table) == [
        [
            "Clubs\xa0\xa0(2)",
        ],
        [
            "OL Bundestag",
        ],
        [
            "Orieentering club",
        ],
    ]

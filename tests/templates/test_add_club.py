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
def club() -> ClubType:
    return ClubType(
        id=7,
        name="OL Bundestag",
    )


def test_club_is_none():
    html = etree.HTML(render.add_club(club=None))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == ""


def test_club_is_not_none(club: ClubType):
    html = etree.HTML(render.add_club(club=club))

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "7"

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "OL Bundestag"

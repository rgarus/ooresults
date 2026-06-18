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


@pytest.fixture()
def competitors() -> list[CompetitorType]:
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


def test_competitor_list_is_not_empty(competitors: list[CompetitorType]) -> None:
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    trs = html.findall(path=".//tbody/tr")
    assert len(trs) == 2

    assert trs[0].attrib["data-id"] == "7"
    tds = html.findall(path=".//tbody/tr[1]/td")
    assert len(tds) == 7
    assert tds[0].text == "Angela"
    assert tds[1].text == "Merkel"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None

    assert trs[1].attrib["data-id"] == "17"
    tds = html.findall(path=".//tbody/tr[2]/td")
    assert len(tds) == 7
    assert tds[0].text == "Birgit"
    assert tds[1].text == "Derkel"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_unknown(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].gender = ""
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        elem = html.find(path=f".//tbody/tr[{i}]/td[3]")
        assert elem.text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_female(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].gender = "F"
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        elem = html.find(path=f".//tbody/tr[{i}]/td[3]")
        if i == row:
            assert elem.text == "F"
        else:
            assert elem.text is None


@pytest.mark.parametrize("row", [1, 2])
def test_gender_is_male(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].gender = "M"
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        elem = html.find(path=f".//tbody/tr[{i}]/td[3]")
        if i == row:
            assert elem.text == "M"
        else:
            assert elem.text is None


@pytest.mark.parametrize("row", [1, 2])
def test_year_is_defined(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].year = 1957
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        elem = html.find(path=f".//tbody/tr[{i}]/td[4]")
        if i == row:
            assert elem.text == "1957"
        else:
            assert elem.text is None


@pytest.mark.parametrize("row", [1, 2])
def test_chip_is_defined(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].chip = "1234567"
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        elem = html.find(path=f".//tbody/tr[{i}]/td[5]")
        if i == row:
            assert elem.text == "1234567"
        else:
            assert elem.text is None


@pytest.mark.parametrize("row", [1, 2])
def test_club_is_defined(competitors: list[CompetitorType], row: int) -> None:
    competitors[row - 1].club_id = 2
    competitors[row - 1].club_name = "OL Bundestag"
    html = Html(text=render.add_entry_competitors(competitors=competitors))

    for i in (1, 2):
        if i == row:
            elem = html.find(path=f".//tbody/tr[{i}]/td[6]")
            assert elem.text == "OL Bundestag"
            elem = html.find(path=f".//tbody/tr[{i}]/td[7]")
            assert elem.text == "2"
        else:
            elem = html.find(path=f".//tbody/tr[{i}]/td[6]")
            assert elem.text is None
            elem = html.find(path=f".//tbody/tr[{i}]/td[7]")
            assert elem.text is None

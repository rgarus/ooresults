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
import tempfile

import pytest
from selenium import webdriver

from webtests.pageobjects.clubs import ClubPage
from webtests.pageobjects.competitors import CompetitorPage
from webtests.pageobjects.tabs import Tabs


@pytest.fixture
def competitor_page(page: webdriver.Remote) -> CompetitorPage:
    Tabs(page=page).select(text="Competitors")
    return CompetitorPage(page=page)


@pytest.fixture
def delete_competitors(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Competitors")
    CompetitorPage(page=page).delete_competitors()
    Tabs(page=page).select(text="Clubs")
    ClubPage(page=page).delete_clubs()
    Tabs(page=page).select(text="Competitors")


def test_import_competitor(competitor_page: CompetitorPage, delete_competitors: None):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CompetitorList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Competitor>
    <Person sex="M">
      <Name>
        <Family>Habeck</Family>
        <Given>Robert</Given>
      </Name>
      <BirthDate>1969-01-01</BirthDate>
    </Person>
    <ControlCard punchingSystem="SI">7509749</ControlCard>
  </Competitor>
    <Competitor>
    <Person sex="F">
      <Name>
        <Family>Bärbock</Family>
        <Given>Anna Lena</Given>
      </Name>
      <BirthDate>1980-01-01</BirthDate>
    </Person>
    <ControlCard punchingSystem="SI">1234567</ControlCard>
  </Competitor>
</CompetitorList>
"""
    dialog = competitor_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "competitors.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_(path=path)

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 3
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (2)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Anna Lena",
        "Bärbock",
        "F",
        "1980",
        "1234567",
        "",
    ]
    assert competitor_page.table.row(i=3) == [
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "",
    ]

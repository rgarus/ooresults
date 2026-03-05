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

from webtests.pageobjects.main_page import MainPage


@pytest.fixture
def delete_clubs(main_page: MainPage) -> None:
    main_page.goto_clubs().delete_clubs()


@pytest.fixture
def add_club(main_page: MainPage, delete_clubs: None) -> None:
    name = "OL Bundestag"

    club_page = main_page.goto_clubs()
    dialog = club_page.actions.add()
    dialog.enter_values(name=name)
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.nr_of_columns() == 1

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
def delete_competitors(main_page: MainPage) -> None:
    main_page.goto_competitors().delete_competitors()


@pytest.fixture
def competitor(main_page: MainPage, delete_competitors: None) -> None:
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender="F",
        year="1980",
        chip="7379879",
        club="",
    )
    dialog.submit()
    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

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


from webtests.pageobjects.main_page import MainPage


def test_if_a_competitor_is_edited_then_the_changed_data_are_displayed(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    competitor_page.table.select_row(2)

    dialog = competitor_page.actions.edit()
    dialog.check_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender="F",
        year="1980",
        chip="7379879",
        club="",
    )
    dialog.enter_values(
        first_name="Anna Lena",
        last_name="Bärbock",
        gender="",
        year="2001",
        chip="1234",
        club="",
    )
    dialog.submit()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (1)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Anna Lena",
        "Bärbock",
        "",
        "2001",
        "1234",
        "",
    ]


def test_if_a_row_is_double_clicked_the_edit_dialog_is_opened(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.table.double_click_row(2)
    dialog.check_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender="F",
        year="1980",
        chip="7379879",
        club="",
    )
    dialog.enter_values(
        first_name="Anna Lena",
        last_name="Bärbock",
        gender="",
        year="2001",
        chip="1234",
        club="",
    )
    dialog.submit()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (1)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Anna Lena",
        "Bärbock",
        "",
        "2001",
        "1234",
        "",
    ]

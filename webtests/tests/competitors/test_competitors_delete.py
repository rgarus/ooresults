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


def test_if_a_competitor_is_deleted_then_the_competitor_is_no_longer_displayed(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()

    # add a second competitor
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club="",
    )
    dialog.submit()

    # select event
    competitor_page.table.select_row(2)

    # delete event
    competitor_page.actions.delete().ok()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (1)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "",
    ]


def test_if_a_competitor_is_deleted_then_no_competitor_is_selected(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()

    # add a second competitor
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club="",
    )
    dialog.submit()

    # select competitor
    competitor_page.table.select_row(2)

    # delete competitor
    competitor_page.actions.delete().ok()
    assert competitor_page.table.selected_row() is None


def test_if_deleting_a_competitor_is_cancelled_then_the_competitor_is_displayed_further(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()

    # select competitor
    competitor_page.table.select_row(2)
    assert competitor_page.table.selected_row() == 2

    # cancel deleting the competitor
    competitor_page.actions.delete().cancel()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.row(i=1) == ["Competitors  (1)"]
    assert competitor_page.table.row(i=2) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
    ]

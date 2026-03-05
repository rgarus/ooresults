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


def test_if_a_competitor_is_added_with_required_data_then_an_additional_competitor_is_displayed(
    main_page: MainPage, delete_competitors: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.check_values(
        first_name="",
        last_name="",
        gender="",
        year="",
        chip="",
        club="",
    )
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="",
        year="",
        chip="",
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
        "Robert",
        "Habeck",
        "",
        "",
        "",
        "",
    ]


def test_if_adding_a_competitor_is_cancelled_then_no_additional_competitor_is_displayed(
    main_page: MainPage, delete_competitors: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club="",
    )
    dialog.cancel()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 0
    assert competitor_page.table.nr_of_columns() == 6


def test_if_a_competitor_is_added_with_all_data_then_an_additional_competitor_is_displayed(
    main_page: MainPage, delete_competitors: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.check_values(
        first_name="",
        last_name="",
        gender="",
        year="",
        chip="",
        club="",
    )
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
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
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "",
    ]


@pytest.mark.parametrize("gender", ["", "F", "M"])
def test_if_a_competitor_is_added_you_can_choose_between_gender_unknown_and_female_and_male(
    gender: str, main_page: MainPage, delete_competitors: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    assert dialog.get_gender_list() == ["", "F", "M"]

    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender=gender,
        year="",
        chip="",
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
        "Robert",
        "Habeck",
        gender,
        "",
        "",
        "",
    ]


def test_if_a_competitor_is_selected_and_a_new_competitor_is_added_then_no_competitor_is_selected(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    competitor_page.table.select_row(i=2)
    assert competitor_page.table.selected_row() == 2

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
    assert competitor_page.table.selected_row() is None


def test_if_several_competitors_are_added_then_the_added_competitors_are_displayed(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Christian",
        last_name="Lindner",
        gender="M",
        year="1979",
        chip="7754987",
        club="",
    )
    dialog.submit()

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

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 4
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (3)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
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
    assert competitor_page.table.row(i=4) == [
        "Christian",
        "Lindner",
        "M",
        "1979",
        "7754987",
        "",
    ]

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
from selenium import webdriver

from webtests.pageobjects.competitors import CompetitorPage
from webtests.pageobjects.tabs import Tabs
from webtests.tests.conftest import post


@pytest.fixture
def competitor_page(page: webdriver.Remote) -> CompetitorPage:
    Tabs(page=page).select(text="Competitors")
    return CompetitorPage(page=page)


@pytest.fixture
def delete_competitors(competitor_page: CompetitorPage) -> None:
    competitor_page.delete_competitors()


@pytest.fixture
def competitor(competitor_page: CompetitorPage, delete_competitors: None) -> None:
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


def test_if_competitor_page_is_displayed_then_all_actions_are_displayed(
    competitor_page: CompetitorPage,
):
    assert competitor_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add competitor ...",
        "Edit competitor ...",
        "Delete competitor",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    competitor_page: CompetitorPage, competitor: None
):
    assert competitor_page.actions.action("Reload").is_enabled()
    assert competitor_page.actions.action("Import ...").is_enabled()
    assert competitor_page.actions.action("Export ...").is_enabled()
    assert competitor_page.actions.action("Add competitor ...").is_enabled()
    assert competitor_page.actions.action("Edit competitor ...").is_disabled()
    assert competitor_page.actions.action("Delete competitor").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    competitor_page: CompetitorPage, competitor: None
):
    competitor_page.table.select_row(i=2)

    assert competitor_page.actions.action("Reload").is_enabled()
    assert competitor_page.actions.action("Import ...").is_enabled()
    assert competitor_page.actions.action("Export ...").is_enabled()
    assert competitor_page.actions.action("Add competitor ...").is_enabled()
    assert competitor_page.actions.action("Edit competitor ...").is_enabled()
    assert competitor_page.actions.action("Delete competitor").is_enabled()


def test_if_competitor_page_is_selected_then_the_table_header_is_displayed(
    competitor_page: CompetitorPage,
):
    assert competitor_page.table.nr_of_columns() == 6
    assert competitor_page.table.headers() == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]


def test_if_a_competitor_is_added_with_required_data_then_an_additional_competitor_is_displayed(
    competitor_page: CompetitorPage, delete_competitors: None
):
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
    competitor_page: CompetitorPage, delete_competitors: None
):
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
    competitor_page: CompetitorPage, delete_competitors: None
):
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
    gender: str, competitor_page: CompetitorPage, delete_competitors: None
):
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


def test_if_no_competitor_is_selected_and_a_new_competitor_is_added_then_no_competitor_is_selected(
    competitor_page: CompetitorPage, competitor: None
):
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


def test_if_a_new_competitor_is_added_then_no_competitor_is_selected(
    competitor_page: CompetitorPage, competitor: None
):
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


def test_if_a_competitor_is_edited_then_the_changed_data_are_displayed(
    competitor_page: CompetitorPage, competitor: None
):
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
    competitor_page: CompetitorPage, competitor: None
):
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


def test_if_a_competitor_is_deleted_then_the_competitor_is_no_longer_displayed(
    competitor_page: CompetitorPage, competitor: None
):
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
    competitor_page: CompetitorPage, competitor: None
):
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
    competitor_page: CompetitorPage, competitor: None
):
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


def test_if_several_competitors_are_added_then_the_added_competitors_are_displayed(
    competitor_page: CompetitorPage, competitor: None
):
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


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    competitor_page: CompetitorPage, competitor: None
):
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

    try:
        competitor_page.filter().set_text("hab")

        # check number of rows
        assert competitor_page.table.nr_of_rows() == 2
        assert competitor_page.table.nr_of_columns() == 6

        assert competitor_page.table.row(i=1) == [
            "Competitors  (3)",
        ]
        assert competitor_page.table.row(i=2) == [
            "Robert",
            "Habeck",
            "M",
            "1969",
            "7509749",
            "",
        ]
    finally:
        competitor_page.filter().set_text("")


def test_if_a_competitor_is_added_by_another_user_then_it_is_displayed_after_reload(
    competitor_page: CompetitorPage, competitor: None
):
    post(
        url="https://127.0.0.1:8080/competitor/add",
        data={
            "id": "",
            "first_name": "Robert",
            "last_name": "Habeck",
            "gender": "M",
            "year": "1969",
            "chip": "7509749",
            "club_id": "",
        },
    )

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (1)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
    ]

    competitor_page.actions.reload()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 3
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (2)",
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

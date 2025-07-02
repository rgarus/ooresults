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

from webtests.pageobjects.clubs import ClubPage
from webtests.pageobjects.tabs import Tabs
from webtests.tests.conftest import post


@pytest.fixture
def club_page(page: webdriver.Remote) -> ClubPage:
    Tabs(page=page).select(text="Clubs")
    return ClubPage(page=page)


@pytest.fixture
def delete_clubs(club_page: ClubPage) -> None:
    club_page.delete_clubs()


@pytest.fixture
def club(club_page: ClubPage, delete_clubs: None) -> None:
    dialog = club_page.actions.add()
    dialog.enter_values(name="OL Bundestag")
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.nr_of_columns() == 1


def test_if_club_page_is_selected_then_all_actions_are_displayed(club_page: ClubPage):
    assert club_page.actions.texts() == [
        "Reload",
        "Add club ...",
        "Edit club ...",
        "Delete club",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    club_page: ClubPage, club: None
):
    assert club_page.table.selected_row() is None

    assert club_page.actions.action("Reload").is_enabled()
    assert club_page.actions.action("Add club ...").is_enabled()
    assert club_page.actions.action("Edit club ...").is_disabled()
    assert club_page.actions.action("Delete club").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    club_page: ClubPage, club: None
):
    club_page.table.select_row(i=2)
    assert club_page.table.selected_row() == 2

    assert club_page.actions.action("Reload").is_enabled()
    assert club_page.actions.action("Add club ...").is_enabled()
    assert club_page.actions.action("Edit club ...").is_enabled()
    assert club_page.actions.action("Delete club").is_enabled()


def test_if_club_page_is_selected_then_table_header_is_displayed(club_page: ClubPage):
    assert club_page.table.nr_of_columns() == 1
    assert club_page.table.headers() == ["Name"]


def test_if_a_club_is_added_with_required_data_then_an_additional_club_is_displayed(
    club_page: ClubPage, delete_clubs: None
):
    dialog = club_page.actions.add()
    dialog.check_values(name="")
    dialog.enter_values(name="OL Bundestag")
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.nr_of_columns() == 1

    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]


def test_if_adding_a_club_is_cancelled_then_no_additional_club_is_displayed(
    club_page: ClubPage, delete_clubs: None
):
    dialog = club_page.actions.add()
    dialog.check_values(name="")
    dialog.enter_values(name="OL Bundestag")
    dialog.cancel()

    # check number of rows
    assert club_page.table.nr_of_rows() == 0
    assert club_page.table.nr_of_columns() == 1


def test_if_a_club_is_added_then_no_club_is_selected(club_page: ClubPage, club: None):
    club_page.table.select_row(i=2)
    assert club_page.table.selected_row() == 2

    dialog = club_page.actions.add()
    dialog.enter_values(name="OC Kanzleramt")
    dialog.submit()

    assert club_page.table.nr_of_rows() == 3
    assert club_page.table.selected_row() is None


def test_if_a_club_is_edited_then_the_changed_data_are_displayed(
    club_page: ClubPage, club: None
):
    club_page.table.select_row(2)

    dialog = club_page.actions.edit()
    dialog.check_values(name="OL Bundestag")
    dialog.enter_values(name="OC Kanzleramt")
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.nr_of_columns() == 1

    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OC Kanzleramt"]


def test_if_a_club_is_edited_then_no_club_is_selected(club_page: ClubPage, club: None):
    club_page.table.select_row(i=2)
    dialog = club_page.actions.edit()
    dialog.check_values(name="OL Bundestag")
    dialog.enter_values(name="OC Kanzleramt")
    dialog.submit()

    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.selected_row() is None


def test_if_a_club_is_deleted_then_the_club_is_no_longer_displayed(
    club_page: ClubPage, club: None
):
    dialog = club_page.actions.add()
    dialog.enter_values(name="XXX Club")
    dialog.submit()

    # select club
    club_page.table.select_row(2)

    # delete club
    club_page.actions.delete().ok()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.selected_row() is None

    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["XXX Club"]


def test_if_a_club_is_deleted_then_no_club_is_selected(club_page: ClubPage, club: None):
    dialog = club_page.actions.add()
    dialog.enter_values(name="XXX Club")
    dialog.submit()

    # select club
    club_page.table.select_row(2)
    assert club_page.table.selected_row() == 2

    # delete club
    club_page.actions.delete().ok()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.selected_row() is None


def test_if_deleting_a_club_is_cancelled_then_the_club_is_displayed_further(
    club_page: ClubPage, club: None
):
    # select club
    club_page.table.select_row(2)
    assert club_page.table.selected_row() == 2

    # delete club
    club_page.actions.delete().cancel()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]


def test_if_several_clubs_are_added_then_the_added_clubs_are_displayed(
    club_page: ClubPage, club: None
):
    dialog = club_page.actions.add()
    dialog.enter_values(name="Verein 2")
    dialog.submit()

    dialog = club_page.actions.add()
    dialog.enter_values(name="Verein 1")
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 4
    assert club_page.table.nr_of_columns() == 1

    assert club_page.table.row(i=1) == ["Clubs  (3)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]
    assert club_page.table.row(i=3) == ["Verein 1"]
    assert club_page.table.row(i=4) == ["Verein 2"]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    club_page: ClubPage, club: None
):
    dialog = club_page.actions.add()
    dialog.enter_values(name="Verein 2")
    dialog.submit()

    dialog = club_page.actions.add()
    dialog.enter_values(name="Verein 1")
    dialog.submit()

    # check number of rows
    assert club_page.table.nr_of_rows() == 4
    assert club_page.table.nr_of_columns() == 1

    try:
        club_page.filter().set_text("bund")

        # check number of rows
        assert club_page.table.nr_of_rows() == 2
        assert club_page.table.nr_of_columns() == 1

        assert club_page.table.row(i=1) == ["Clubs  (3)"]
        assert club_page.table.row(i=2) == ["OL Bundestag"]
    finally:
        club_page.filter().set_text("")


def test_if_an_club_is_added_by_another_user_then_it_is_displayed_after_reload(
    club_page: ClubPage, club: None
):
    post(
        url="https://127.0.0.1:8080/club/add",
        data={
            "id": "",
            "name": "XXX Club",
        },
    )

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.nr_of_columns() == 1

    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]

    club_page.actions.reload()

    # check number of rows
    assert club_page.table.nr_of_rows() == 3
    assert club_page.table.nr_of_columns() == 1

    assert club_page.table.row(i=1) == ["Clubs  (2)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]
    assert club_page.table.row(i=3) == ["XXX Club"]

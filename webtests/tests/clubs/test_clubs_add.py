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


from webtests.controls.alert_window import AlertWindow
from webtests.pageobjects.main_page import MainPage


def test_if_a_club_is_added_with_required_data_then_an_additional_club_is_displayed(
    main_page: MainPage, delete_clubs: None
):
    club_page = main_page.goto_clubs()
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
    main_page: MainPage, delete_clubs: None
):
    club_page = main_page.goto_clubs()
    dialog = club_page.actions.add()
    dialog.check_values(name="")
    dialog.enter_values(name="OL Bundestag")
    dialog.cancel()

    # check number of rows
    assert club_page.table.nr_of_rows() == 0
    assert club_page.table.nr_of_columns() == 1


def test_if_a_club_is_added_then_no_club_is_selected(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
    club_page.table.select_row(i=2)
    assert club_page.table.selected_row() == 2

    dialog = club_page.actions.add()
    dialog.enter_values(name="OC Kanzleramt")
    dialog.submit()

    assert club_page.table.nr_of_rows() == 3
    assert club_page.table.selected_row() is None


def test_if_several_clubs_are_added_then_the_added_clubs_are_displayed(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
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


def test_if_a_club_is_added_a_second_time_then_an_error_message_will_be_displayed(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()

    # add the club a second time
    dialog = club_page.actions.add()
    dialog.enter_values(name="OL Bundestag")
    dialog.submit(wait_until_closed=False)

    # check error message
    alert = AlertWindow(driver=club_page.driver)
    assert alert.get_text() == "Club already exist"
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]

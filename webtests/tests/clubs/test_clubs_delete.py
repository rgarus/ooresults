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


def test_if_a_club_is_deleted_then_the_club_is_no_longer_displayed(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
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


def test_if_a_club_is_deleted_then_no_club_is_selected(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
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
    main_page: MainPage, add_club: None
):
    # select club
    club_page = main_page.goto_clubs()
    club_page.table.select_row(2)
    assert club_page.table.selected_row() == 2

    # delete club
    club_page.actions.delete().cancel()

    # check number of rows
    assert club_page.table.nr_of_rows() == 2
    assert club_page.table.row(i=1) == ["Clubs  (1)"]
    assert club_page.table.row(i=2) == ["OL Bundestag"]

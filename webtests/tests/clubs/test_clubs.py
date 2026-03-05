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


def test_if_club_page_is_selected_then_all_actions_are_displayed(main_page: MainPage):
    club_page = main_page.goto_clubs()
    assert club_page.actions.texts() == [
        "Reload",
        "Add club ...",
        "Edit club ...",
        "Delete club",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
    assert club_page.table.selected_row() is None

    assert club_page.actions.action("Reload").is_enabled()
    assert club_page.actions.action("Add club ...").is_enabled()
    assert club_page.actions.action("Edit club ...").is_disabled()
    assert club_page.actions.action("Delete club").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    main_page: MainPage, add_club: None
):
    club_page = main_page.goto_clubs()
    club_page.table.select_row(i=2)
    assert club_page.table.selected_row() == 2

    assert club_page.actions.action("Reload").is_enabled()
    assert club_page.actions.action("Add club ...").is_enabled()
    assert club_page.actions.action("Edit club ...").is_enabled()
    assert club_page.actions.action("Delete club").is_enabled()


def test_if_club_page_is_selected_then_table_header_is_displayed(main_page: MainPage):
    club_page = main_page.goto_clubs()
    assert club_page.table.nr_of_columns() == 1
    assert club_page.table.headers() == ["Name"]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
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

    try:
        club_page.filter().set_text("bund")

        # check number of rows
        assert club_page.table.nr_of_rows() == 2
        assert club_page.table.nr_of_columns() == 1

        assert club_page.table.row(i=1) == ["Clubs  (3)"]
        assert club_page.table.row(i=2) == ["OL Bundestag"]
    finally:
        club_page.filter().set_text("")

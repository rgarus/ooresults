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


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-12-28"


def test_if_an_entry_is_deleted_then_the_entry_is_no_longer_displayed(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)

    # add a second entry
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Nancy", last_name="Faeser", class_name="Bahn A - Frauen"
    )
    dialog.submit()
    assert entry_page.table.nr_of_rows() == 3

    # select entry
    entry_page.table.select_row(3)
    # delete entry
    entry_page.actions.delete().ok()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]


def test_if_an_entry_is_deleted_then_no_entry_is_selected(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)

    # add a second entry
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Nancy", last_name="Faeser", class_name="Bahn A - Frauen"
    )
    dialog.submit()

    # select entry
    entry_page.table.select_row(2)
    # delete entry
    entry_page.actions.delete().ok()

    assert entry_page.table.selected_row() is None


def test_if_deleting_an_entry_is_cancelled_then_the_entry_is_displayed_further(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)

    # select entry
    entry_page.table.select_row(2)
    assert entry_page.table.selected_row() == 2

    # cancel deleting the entry
    entry_page.actions.delete().cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.row(i=1) == ["Entries  (1)"]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]

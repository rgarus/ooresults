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


def test_if_entry_page_is_displayed_then_all_actions_are_displayed(
    main_page: MainPage, event: str
):
    entry_page = main_page.goto_entries(event=event)
    assert entry_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add entry ...",
        "Edit entry ...",
        "Delete entry",
        "Edit split times ...",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    main_page: MainPage, event: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    assert entry_page.actions.action("Reload").is_enabled()
    assert entry_page.actions.action("Import ...").is_enabled()
    assert entry_page.actions.action("Export ...").is_enabled()
    assert entry_page.actions.action("Add entry ...").is_enabled()
    assert entry_page.actions.action("Edit entry ...").is_disabled()
    assert entry_page.actions.action("Delete entry").is_disabled()
    assert entry_page.actions.action("Edit split times ...").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    main_page: MainPage, event: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    entry_page.table.select_row(i=2)

    assert entry_page.actions.action("Reload").is_enabled()
    assert entry_page.actions.action("Import ...").is_enabled()
    assert entry_page.actions.action("Export ...").is_enabled()
    assert entry_page.actions.action("Add entry ...").is_enabled()
    assert entry_page.actions.action("Edit entry ...").is_enabled()
    assert entry_page.actions.action("Delete entry").is_enabled()
    assert entry_page.actions.action("Edit split times ...").is_enabled()


def test_if_entry_page_is_selected_then_the_table_header_is_displayed(
    main_page: MainPage, event: str
):
    entry_page = main_page.goto_entries(event=event)
    assert entry_page.table.nr_of_columns() == 11
    assert entry_page.table.headers() == [
        "  NC  ",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Olaf",
        last_name="Scholz",
        gender="M",
        year="1959",
        chip="7579050",
        club_name="",
        class_name="Bahn A - Männer",
        not_competing=False,
        start_time="11:00:03",
        status="",
    )
    dialog.submit()

    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club_name="",
        class_name="Bahn A - Männer",
        not_competing=False,
        start_time="11:00:06",
        status="",
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 4
    assert entry_page.table.nr_of_columns() == 11

    try:
        entry_page.filter().set_text("1969")

        # check number of rows
        assert entry_page.table.nr_of_rows() == 2
        assert entry_page.table.nr_of_columns() == 11

        assert entry_page.table.row(i=1) == [
            "Entries  (3)",
        ]
        assert entry_page.table.row(i=2) == [
            "",
            "Robert",
            "Habeck",
            "M",
            "1969",
            "7509749",
            "",
            "Bahn A - Männer",
            "11:00:06",
            "",
            "",
        ]
    finally:
        entry_page.filter().set_text("")

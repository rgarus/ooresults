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


EVENT_NAME = "Test for Classes"
EVENT_DATE = "2023-12-28"


def test_if_class_page_is_displayed_then_all_actions_are_displayed(
    main_page: MainPage, event: str
):
    assert main_page.goto_classes(event=event).actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add class ...",
        "Edit class ...",
        "Delete class",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)

    assert class_page.actions.action("Reload").is_enabled()
    assert class_page.actions.action("Import ...").is_enabled()
    assert class_page.actions.action("Export ...").is_enabled()
    assert class_page.actions.action("Add class ...").is_enabled()
    assert class_page.actions.action("Edit class ...").is_disabled()
    assert class_page.actions.action("Delete class").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
    class_page.table.select_row(i=2)

    assert class_page.actions.action("Reload").is_enabled()
    assert class_page.actions.action("Import ...").is_enabled()
    assert class_page.actions.action("Export ...").is_enabled()
    assert class_page.actions.action("Add class ...").is_enabled()
    assert class_page.actions.action("Edit class ...").is_enabled()
    assert class_page.actions.action("Delete class").is_enabled()


def test_if_class_page_is_selected_then_the_table_header_is_displayed(
    main_page: MainPage, event: str
):
    class_page = main_page.goto_classes(event=event)
    assert class_page.table.nr_of_columns() == 11
    assert class_page.table.headers() == [
        "Name",
        "Short name",
        "Course",
        "Voided legs",
        "Type",
        "Use start control",
        "Apply handicap",
        "Mass start",
        "Time limit",
        "Penalty controls",
        "Penalty time limit",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
    )
    dialog.submit()

    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Men Short",
        short_name="MS",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 4
    assert class_page.table.nr_of_columns() == 11

    try:
        class_page.filter().set_text("WS")

        # check number of rows
        assert class_page.table.nr_of_rows() == 2
        assert class_page.table.nr_of_columns() == 11

        assert class_page.table.row(i=1) == [
            "Classes  (3)",
        ]
        assert class_page.table.row(i=2) == [
            "Women Short",
            "WS",
            "",
            "100-101",
            "Net",
            "Yes",
            "Yes",
            "12:30:00",
            "30:00",
            "400",
            "500",
        ]
    finally:
        class_page.filter().set_text("")

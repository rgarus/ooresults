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


EVENT_NAME = "Test for Courses"
EVENT_DATE = "2023-12-28"


def test_if_course_page_is_displayed_then_all_actions_are_displayed(
    main_page: MainPage, event: str
):
    course_page = main_page.goto_courses(event=event)
    assert course_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add course ...",
        "Edit course ...",
        "Delete course",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    assert course_page.actions.action("Reload").is_enabled()
    assert course_page.actions.action("Import ...").is_enabled()
    assert course_page.actions.action("Export ...").is_enabled()
    assert course_page.actions.action("Add course ...").is_enabled()
    assert course_page.actions.action("Edit course ...").is_disabled()
    assert course_page.actions.action("Delete course").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    course_page.table.select_row(i=2)

    assert course_page.actions.action("Reload").is_enabled()
    assert course_page.actions.action("Import ...").is_enabled()
    assert course_page.actions.action("Export ...").is_enabled()
    assert course_page.actions.action("Add course ...").is_enabled()
    assert course_page.actions.action("Edit course ...").is_enabled()
    assert course_page.actions.action("Delete course").is_enabled()


def test_if_course_page_is_selected_then_the_table_header_is_displayed(
    main_page: MainPage, event: str
):
    course_page = main_page.goto_courses(event=event)
    assert course_page.table.nr_of_columns() == 4
    assert course_page.table.headers() == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn C",
        length="",
        climb="",
        controls="130-131-132",
    )
    dialog.submit()

    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="121-124-122-123",
    )
    dialog.submit()

    # check number of rows
    assert course_page.table.nr_of_rows() == 4
    assert course_page.table.nr_of_columns() == 4

    try:
        course_page.filter().set_text("Bahn B")

        # check number of rows
        assert course_page.table.nr_of_rows() == 2
        assert course_page.table.nr_of_columns() == 4

        assert course_page.table.row(i=1) == [
            "Courses  (3)",
        ]
        assert course_page.table.row(i=2) == [
            "Bahn B",
            "4500",
            "60",
            "122 - 123 - 124 - 125 - 121",
        ]
    finally:
        course_page.filter().set_text("")

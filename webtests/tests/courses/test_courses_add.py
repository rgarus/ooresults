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


def test_if_a_course_is_added_with_required_data_then_an_additional_course_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
):
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.add()
    dialog.check_values(
        name="",
        length="",
        climb="",
        controls="",
    )
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="",
    )
    dialog.submit()

    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4

    assert course_page.table.row(i=1) == [
        "Courses  (1)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn A",
        "",
        "",
        "",
    ]


def test_if_adding_a_course_is_cancelled_then_no_additional_course_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
):
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="121-124-122-123",
    )
    dialog.cancel()

    # check number of rows
    assert course_page.table.nr_of_rows() == 0
    assert course_page.table.nr_of_columns() == 4


def test_if_a_course_is_added_with_all_data_then_an_additional_course_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
):
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.add()
    dialog.check_values(
        name="",
        length="",
        climb="",
        controls="",
    )
    dialog.enter_values(
        name="Bahn B",
        length="3600",
        climb="75",
        controls="121-124-122-123",
    )
    dialog.submit()

    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4

    assert course_page.table.row(i=1) == [
        "Courses  (1)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn B",
        "3600",
        "75",
        "121 - 124 - 122 - 123",
    ]


def test_if_a_course_is_selected_and_a_new_course_is_added_then_no_course_is_selected(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    course_page.table.select_row(i=2)
    assert course_page.table.selected_row() == 2

    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="121-124-122-123",
    )
    dialog.submit()
    assert course_page.table.selected_row() is None


def test_if_several_courses_are_added_then_the_added_courses_are_displayed(
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

    assert course_page.table.row(i=1) == [
        "Courses  (3)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn A",
        "",
        "",
        "121 - 124 - 122 - 123",
    ]
    assert course_page.table.row(i=3) == [
        "Bahn B",
        "4500",
        "60",
        "122 - 123 - 124 - 125 - 121",
    ]
    assert course_page.table.row(i=4) == [
        "Bahn C",
        "",
        "",
        "130 - 131 - 132",
    ]

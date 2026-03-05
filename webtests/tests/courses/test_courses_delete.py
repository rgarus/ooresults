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


def test_if_a_course_is_deleted_then_the_course_is_no_longer_displayed(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)

    # add a second course
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="121-124-122-123",
    )
    dialog.submit()

    # select course
    course_page.table.select_row(3)

    # delete course
    course_page.actions.delete().ok()

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
        "121 - 124 - 122 - 123",
    ]


def test_if_a_course_is_deleted_then_no_course_is_selected(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)

    # add a second course
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn A",
        length="",
        climb="",
        controls="121-124-122-123",
    )
    dialog.submit()

    # select course
    course_page.table.select_row(2)

    # delete course
    course_page.actions.delete().ok()
    assert course_page.table.selected_row() is None


def test_if_deleting_a_course_is_cancelled_then_the_course_is_displayed_further(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)

    # select course
    course_page.table.select_row(2)
    assert course_page.table.selected_row() == 2

    # cancel deleting the course
    course_page.actions.delete().cancel()

    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.row(i=1) == ["Courses  (1)"]
    assert course_page.table.row(i=2) == [
        "Bahn B",
        "4500",
        "60",
        "122 - 123 - 124 - 125 - 121",
    ]

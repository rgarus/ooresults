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


def test_if_a_course_is_edited_then_the_changed_data_are_displayed(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    course_page.table.select_row(2)

    dialog = course_page.actions.edit()
    dialog.check_values(
        name="Bahn B",
        length="4500",
        climb="60",
        controls="122 - 123 - 124 - 125 - 121",
    )
    dialog.enter_values(
        name="Bahn easy",
        length="4650",
        climb="45",
        controls="122 - 124 - 125",
    )
    dialog.submit()

    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4

    assert course_page.table.row(i=1) == [
        "Courses  (1)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn easy",
        "4650",
        "45",
        "122 - 124 - 125",
    ]


def test_if_a_row_is_double_clicked_the_edit_dialog_is_opened(
    main_page: MainPage, event: str, course: None
):
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.table.double_click_row(2)
    dialog.check_values(
        name="Bahn B",
        length="4500",
        climb="60",
        controls="122 - 123 - 124 - 125 - 121",
    )
    dialog.enter_values(
        name="Bahn easy",
        length="4650",
        climb="45",
        controls="122 - 124 - 125",
    )
    dialog.submit()

    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4

    assert course_page.table.row(i=1) == [
        "Courses  (1)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn easy",
        "4650",
        "45",
        "122 - 124 - 125",
    ]

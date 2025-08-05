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


import pytest
from selenium import webdriver

from webtests.pageobjects.courses import CoursePage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs


EVENT_NAME = "Test for Courses"
EVENT_DATE = "2023-12-28"


@pytest.fixture(scope="module")
def select_event(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()
    dialog = event_page.actions.add()
    dialog.enter_values(
        name=EVENT_NAME,
        date=EVENT_DATE,
    )
    dialog.submit()
    event_page.table.select_row(2)
    yield
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()


@pytest.fixture
def course_page(page: webdriver.Remote, select_event: None) -> CoursePage:
    Tabs(page=page).select(text="Courses")
    return CoursePage(page=page)


@pytest.fixture
def delete_courses(course_page: CoursePage) -> None:
    course_page.delete_courses()


@pytest.fixture
def course(course_page: CoursePage, delete_courses: None) -> None:
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn B",
        length="4500",
        climb="60",
        controls="122-123-124-125-121",
    )
    dialog.submit()
    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4


def test_if_course_page_is_displayed_then_all_actions_are_displayed(
    course_page: CoursePage,
):
    assert course_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add course ...",
        "Edit course ...",
        "Delete course",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    course_page: CoursePage, course: None
):
    assert course_page.actions.action("Reload").is_enabled()
    assert course_page.actions.action("Import ...").is_enabled()
    assert course_page.actions.action("Export ...").is_enabled()
    assert course_page.actions.action("Add course ...").is_enabled()
    assert course_page.actions.action("Edit course ...").is_disabled()
    assert course_page.actions.action("Delete course").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    course_page: CoursePage, course: None
):
    course_page.table.select_row(i=2)

    assert course_page.actions.action("Reload").is_enabled()
    assert course_page.actions.action("Import ...").is_enabled()
    assert course_page.actions.action("Export ...").is_enabled()
    assert course_page.actions.action("Add course ...").is_enabled()
    assert course_page.actions.action("Edit course ...").is_enabled()
    assert course_page.actions.action("Delete course").is_enabled()


def test_if_course_page_is_selected_then_the_table_header_is_displayed(
    course_page: CoursePage,
):
    assert course_page.table.nr_of_columns() == 4
    assert course_page.table.headers() == [
        "Name",
        "Length",
        "Climb",
        "Controls",
    ]


def test_if_a_course_is_added_with_required_data_then_an_additional_course_is_displayed(
    course_page: CoursePage, delete_courses: None
):
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
    course_page: CoursePage, delete_courses: None
):
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
    course_page: CoursePage, delete_courses: None
):
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
    course_page: CoursePage, course: None
):
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


def test_if_a_course_is_edited_then_the_changed_data_are_displayed(
    course_page: CoursePage, course: None
):
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
    course_page: CoursePage, course: None
):
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


def test_if_a_course_is_deleted_then_the_course_is_no_longer_displayed(
    course_page: CoursePage, course: None
):
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
    course_page: CoursePage, course: None
):
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
    course_page: CoursePage, course: None
):
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


def test_if_several_courses_are_added_then_the_added_courses_are_displayed(
    course_page: CoursePage, course: None
):
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


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    course_page: CoursePage, course: None
):
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

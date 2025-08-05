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

from webtests.pageobjects.classes import ClassPage
from webtests.pageobjects.courses import CoursePage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs


EVENT_NAME = "Test for Classes"
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


@pytest.fixture(scope="module")
def add_courses(page: webdriver.Remote, select_event: None) -> None:
    Tabs(page=page).select(text="Courses")
    course_page = CoursePage(page=page)
    course_page.delete_courses()
    dialog = course_page.actions.add()
    dialog.enter_values(name="Bahn A")
    dialog.submit()
    dialog = course_page.actions.add()
    dialog.enter_values(name="Bahn B")
    dialog.submit()


@pytest.fixture
def class_page(page: webdriver.Remote, add_courses: None) -> ClassPage:
    Tabs(page=page).select(text="Classes")
    return ClassPage(page=page)


@pytest.fixture
def delete_classes(class_page: ClassPage) -> None:
    class_page.delete_classes()


@pytest.fixture
def class_(class_page: ClassPage, delete_classes: None) -> None:
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Short",
        short_name="WS",
        course="",
        voided_legs="100-101",
        type="Net",
        use_start_control="Yes",
        apply_handicap=True,
        mass_start="12:30:00",
        time_limit="30:00",
        penalty_controls="400",
        penalty_time_limit="500",
    )
    dialog.submit()
    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11


def test_if_class_page_is_displayed_then_all_actions_are_displayed(
    class_page: ClassPage,
):
    assert class_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add class ...",
        "Edit class ...",
        "Delete class",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    class_page: ClassPage, class_: None
):
    assert class_page.actions.action("Reload").is_enabled()
    assert class_page.actions.action("Import ...").is_enabled()
    assert class_page.actions.action("Export ...").is_enabled()
    assert class_page.actions.action("Add class ...").is_enabled()
    assert class_page.actions.action("Edit class ...").is_disabled()
    assert class_page.actions.action("Delete class").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    class_page: ClassPage, class_: None
):
    class_page.table.select_row(i=2)

    assert class_page.actions.action("Reload").is_enabled()
    assert class_page.actions.action("Import ...").is_enabled()
    assert class_page.actions.action("Export ...").is_enabled()
    assert class_page.actions.action("Add class ...").is_enabled()
    assert class_page.actions.action("Edit class ...").is_enabled()
    assert class_page.actions.action("Delete class").is_enabled()


def test_if_class_page_is_selected_then_the_table_header_is_displayed(
    class_page: ClassPage,
):
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


def test_if_a_class_is_added_with_required_data_then_an_additional_class_is_displayed(
    class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    dialog.check_values(
        name="",
        short_name="",
        course="",
        voided_legs="",
        type="Standard",
        use_start_control="If punched",
        apply_handicap=False,
        mass_start="",
        time_limit="",
        penalty_controls="",
        penalty_time_limit="",
    )
    dialog.enter_values(
        name="Women Long",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women Long",
        "",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]


def test_if_adding_a_class_is_cancelled_then_no_additional_class_is_displayed(
    class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
        course="",
        voided_legs="",
        type="Standard",
        use_start_control="If punched",
        apply_handicap=False,
        mass_start="",
        time_limit="45:00",
        penalty_controls="",
        penalty_time_limit="",
    )
    dialog.cancel()

    # check number of rows
    assert class_page.table.nr_of_rows() == 0
    assert class_page.table.nr_of_columns() == 11


def test_if_a_class_is_added_with_all_data_then_an_additional_class_is_displayed(
    class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    dialog.check_values(
        name="",
        short_name="",
        course="",
        voided_legs="",
        type="Standard",
        use_start_control="If punched",
        apply_handicap=False,
        mass_start="",
        time_limit="",
        penalty_controls="",
        penalty_time_limit="",
    )
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
        course="",
        voided_legs="100-101",
        type="Net",
        use_start_control="Yes",
        apply_handicap=True,
        mass_start="12:30:00",
        time_limit="30:00",
        penalty_controls="400",
        penalty_time_limit="500",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women Long",
        "WL",
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


@pytest.mark.parametrize("course", ["Bahn A", "Bahn B"])
def test_if_a_class_is_added_you_can_choose_between_all_defined_courses(
    course: str, class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    assert dialog.get_course_list() == ["", "Bahn A", "Bahn B"]

    dialog.enter_values(
        name="Women Long",
        course=course,
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women Long",
        "",
        course,
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]


@pytest.mark.parametrize("type", ["Standard", "Net", "Score"])
def test_if_a_class_is_added_you_can_choose_between_type_standard_and_net_and_score(
    type: str, class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    assert dialog.get_type_list() == ["Standard", "Net", "Score"]

    dialog.enter_values(
        name="Women Long",
        type=type,
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women Long",
        "",
        "",
        "",
        type,
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]


@pytest.mark.parametrize("use_start_control", ["If punched", "No", "Yes"])
def test_if_a_class_is_added_you_can_choose_between_use_start_control_if_punched_and_no_and_yes(
    use_start_control: str, class_page: ClassPage, delete_classes: None
):
    dialog = class_page.actions.add()
    assert dialog.get_use_start_control_list() == ["If punched", "No", "Yes"]

    dialog.enter_values(
        name="Women Long",
        use_start_control=use_start_control,
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women Long",
        "",
        "",
        "",
        "Standard",
        use_start_control,
        "",
        "",
        "",
        "",
        "",
    ]


def test_if_a_class_is_selected_and_a_new_class_is_added_then_no_class_is_selected(
    class_page: ClassPage, class_: None
):
    class_page.table.select_row(i=2)
    assert class_page.table.selected_row() == 2

    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
    )
    dialog.submit()
    assert class_page.table.selected_row() is None


def test_if_a_class_is_edited_then_the_changed_data_are_displayed(
    class_page: ClassPage, class_: None
):
    class_page.table.select_row(2)

    dialog = class_page.actions.edit()
    dialog.check_values(
        name="Women Short",
        short_name="WS",
        course="",
        voided_legs="100-101",
        type="Net",
        use_start_control="Yes",
        apply_handicap=True,
        mass_start="12:30:00",
        time_limit="30:00",
        penalty_controls="400",
        penalty_time_limit="500",
    )
    dialog.enter_values(
        name="Women (Short)",
        short_name="W-S",
        course="",
        voided_legs="221-222, 235-230",
        type="Score",
        use_start_control="No",
        apply_handicap=False,
        mass_start="10:21:30",
        time_limit="45:15",
        penalty_controls="210",
        penalty_time_limit="300",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women (Short)",
        "W-S",
        "",
        "221-222, 235-230",
        "Score",
        "No",
        "",
        "10:21:30",
        "45:15",
        "210",
        "300",
    ]


def test_if_a_row_is_double_clicked_the_edit_dialog_is_opened(
    class_page: ClassPage, class_: None
):
    dialog = class_page.table.double_click_row(2)
    dialog.check_values(
        name="Women Short",
        short_name="WS",
        course="",
        voided_legs="100-101",
        type="Net",
        use_start_control="Yes",
        apply_handicap=True,
        mass_start="12:30:00",
        time_limit="30:00",
        penalty_controls="400",
        penalty_time_limit="500",
    )
    dialog.enter_values(
        name="Women (Short)",
        short_name="W-S",
        course="",
        voided_legs="221-222, 235-230",
        type="Score",
        use_start_control="No",
        apply_handicap=False,
        mass_start="10:21:30",
        time_limit="45:15",
        penalty_controls="210",
        penalty_time_limit="300",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
    ]
    assert class_page.table.row(i=2) == [
        "Women (Short)",
        "W-S",
        "",
        "221-222, 235-230",
        "Score",
        "No",
        "",
        "10:21:30",
        "45:15",
        "210",
        "300",
    ]


def test_if_a_class_is_deleted_then_the_class_is_no_longer_displayed(
    class_page: ClassPage, class_: None
):
    # add a second course
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
        course="",
        voided_legs="221-222, 235-230",
        type="Score",
        use_start_control="No",
        apply_handicap=False,
        mass_start="10:21:30",
        time_limit="45:15",
        penalty_controls="210",
        penalty_time_limit="300",
    )
    dialog.submit()

    # select course
    class_page.table.select_row(2)

    # delete course
    class_page.actions.delete().ok()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (1)",
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


def test_if_a_class_is_deleted_then_no_class_is_selected(
    class_page: ClassPage, class_: None
):
    # add a second course
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
    )
    dialog.submit()

    # select course
    class_page.table.select_row(2)

    # delete course
    class_page.actions.delete().ok()
    assert class_page.table.selected_row() is None


def test_if_deleting_a_class_is_cancelled_then_the_class_is_displayed_further(
    class_page: ClassPage, class_: None
):
    # select course
    class_page.table.select_row(2)
    assert class_page.table.selected_row() == 2

    # cancel deleting the course
    class_page.actions.delete().cancel()

    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.row(i=1) == ["Classes  (1)"]
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


def test_if_several_classes_are_added_then_the_added_classes_are_displayed(
    class_page: ClassPage, class_: None
):
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

    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Men Long",
        short_name="ML",
    )
    dialog.submit()

    # check number of rows
    assert class_page.table.nr_of_rows() == 5
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (4)",
    ]
    assert class_page.table.row(i=2) == [
        "Men Long",
        "ML",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]
    assert class_page.table.row(i=3) == [
        "Men Short",
        "MS",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]
    assert class_page.table.row(i=4) == [
        "Women Long",
        "WL",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]
    assert class_page.table.row(i=5) == [
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


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    class_page: ClassPage, class_: None
):
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

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

from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Classes"
EVENT_DATE = "2023-12-28"


def test_if_a_class_is_added_with_required_data_then_an_additional_class_is_displayed(
    main_page: MainPage, event: str, delete_classes: None
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, delete_classes: None
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, delete_classes: None
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage,
    event: str,
    delete_classes: None,
    add_courses: None,
    course: str,
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage,
    event: str,
    delete_classes: None,
    type: str,
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, delete_classes: None, use_start_control: str
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, add_class: None
):
    class_page = main_page.goto_classes(event=event)
    class_page.table.select_row(i=2)
    assert class_page.table.selected_row() == 2

    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Long",
        short_name="WL",
    )
    dialog.submit()
    assert class_page.table.selected_row() is None


def test_if_several_classes_are_added_then_the_added_classes_are_displayed(
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

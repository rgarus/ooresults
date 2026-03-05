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


def test_if_a_class_is_deleted_then_the_class_is_no_longer_displayed(
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
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

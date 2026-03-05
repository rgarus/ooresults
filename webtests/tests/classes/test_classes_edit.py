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


def test_if_a_class_is_edited_then_the_changed_data_are_displayed(
    main_page: MainPage, event: str, add_class: None
):
    class_page = main_page.goto_classes(event=event)
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
    main_page: MainPage, event: str, add_class: str
):
    class_page = main_page.goto_classes(event=event)
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

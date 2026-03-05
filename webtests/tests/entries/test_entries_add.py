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

from webtests.pageobjects.entries import StatusDialog
from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-12-28"


def test_if_an_entry_is_added_with_required_data_then_an_additional_entry_is_displayed(
    main_page: MainPage,
    event: str,
    add_classes: str,
    delete_entries_and_competitors: None,
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.check_values(
        first_name="",
        last_name="",
        gender="",
        year="",
        chip="",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=False,
        start_time="",
        status="",
    )
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        class_name="Bahn A - Frauen",
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "",
        "",
        "",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


def test_if_adding_an_entry_is_cancelled_then_no_additional_entry_is_displayed(
    main_page: MainPage,
    event: str,
    add_classes: str,
    delete_entries_and_competitors: None,
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender="F",
        year="1980",
        chip="7379879",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=False,
        start_time="11:00:00",
        status="",
    )
    dialog.cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 0
    assert entry_page.table.nr_of_columns() == 11


def test_if_an_entry_is_added_with_all_data_then_an_additional_entry_is_displayed(
    main_page: MainPage,
    event: str,
    add_classes: str,
    delete_entries_and_competitors: None,
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.check_values(
        first_name="",
        last_name="",
        gender="",
        year="",
        chip="",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=False,
        start_time="",
        status="",
    )
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender="F",
        year="1980",
        chip="7379879",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=True,
        start_time="11:00:00",
        status="",
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "X",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]


def test_if_an_already_registered_competitor_is_added_with_not_competing_true_then_an_additional_entry_is_displayed(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        class_name="Bahn A - Frauen",
        not_competing=True,
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 3
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (2)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]
    assert entry_page.table.row(i=3) == [
        "X",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


def test_if_an_already_registered_competitor_is_added_with_not_competing_false_then_not_competing_is_set_to_true(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        class_name="Bahn A - Frauen",
        not_competing=False,
    )
    dialog.submit(wait_until_closed=False)
    info_dialog = StatusDialog(driver=main_page.driver).wait()
    assert info_dialog.get_text() == [
        "Warning:",
        'The participant is already registered for this event. Therefore, the competing status has been changed to “not competing".',
        "However, you can change this at any time.",
    ]
    info_dialog.close()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 3
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (2)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]
    assert entry_page.table.row(i=3) == [
        "X",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


@pytest.mark.parametrize("gender", ["", "F", "M"])
def test_if_an_entry_is_added_you_can_choose_between_gender_unknown_and_female_and_male(
    gender: str,
    main_page: MainPage,
    event: str,
    add_classes: str,
    delete_entries_and_competitors: None,
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    assert dialog.get_gender_list() == ["", "F", "M"]

    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        gender=gender,
        class_name="Bahn A - Frauen",
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        gender,
        "",
        "",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


@pytest.mark.parametrize("class_name", ["Bahn A - Frauen", "Bahn A - Männer"])
def test_if_an_entry_is_added_you_can_choose_between_all_defined_classes(
    class_name: str,
    main_page: MainPage,
    event: str,
    add_classes: str,
    delete_entries_and_competitors: None,
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    assert dialog.get_class_list() == ["Bahn A - Frauen", "Bahn A - Männer"]

    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        class_name=class_name,
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "",
        "",
        "",
        "",
        class_name,
        "",
        "",
        "",
    ]


def test_if_an_entry_is_selected_and_a_new_entry_is_added_then_no_entry_is_selected(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    nr_of_rows = entry_page.table.nr_of_rows()
    entry_page.table.select_row(i=2)
    assert entry_page.table.selected_row() == 2

    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Nancy", last_name="Faeser", class_name="Bahn A - Frauen"
    )
    dialog.submit()
    assert entry_page.table.nr_of_rows() == nr_of_rows + 1
    assert entry_page.table.selected_row() is None


def test_if_several_entries_are_added_then_the_added_entries_are_displayed(
    main_page: MainPage, event: str, add_classes: str, entry: None
):
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Olaf",
        last_name="Scholz",
        gender="M",
        year="1958",
        chip="7579050",
        club_name="",
        class_name="Bahn A - Männer",
        not_competing=False,
        start_time="11:00:03",
        status="",
    )
    dialog.submit()

    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club_name="",
        class_name="Bahn A - Männer",
        not_competing=False,
        start_time="11:00:06",
        status="",
    )
    dialog.submit()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 4
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (3)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]
    assert entry_page.table.row(i=3) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "",
        "Bahn A - Männer",
        "11:00:06",
        "",
        "",
    ]
    assert entry_page.table.row(i=4) == [
        "",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "",
        "Bahn A - Männer",
        "11:00:03",
        "",
        "",
    ]

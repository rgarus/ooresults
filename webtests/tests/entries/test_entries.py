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

from webtests.controls.alert_window import AlertWindow
from webtests.pageobjects.classes import ClassPage
from webtests.pageobjects.competitors import CompetitorPage
from webtests.pageobjects.entries import EntryPage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-12-28"


@pytest.fixture(scope="module")
def select_event(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE)
    dialog.submit()
    event_page.table.select_row(2)
    yield
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()


@pytest.fixture(scope="module")
def add_classes(page: webdriver.Remote, select_event: None) -> None:
    Tabs(page=page).select(text="Classes")
    class_page = ClassPage(page=page)
    class_page.delete_classes()
    dialog = class_page.actions.add()
    dialog.enter_values(name="Bahn A - Frauen")
    dialog.submit()
    dialog = class_page.actions.add()
    dialog.enter_values(name="Bahn A - Männer")
    dialog.submit()


@pytest.fixture
def entry_page(page: webdriver.Remote, add_classes: None) -> EntryPage:
    Tabs(page=page).select(text="Entries")
    return EntryPage(page=page)


@pytest.fixture
def delete_entries(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Entries")
    EntryPage(page=page).delete_entries()
    Tabs(page=page).select(text="Competitors")
    CompetitorPage(page=page).delete_competitors()
    Tabs(page=page).select(text="Entries")


@pytest.fixture
def entry(entry_page: EntryPage, delete_entries: None) -> None:
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
    dialog.submit()
    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11


def test_if_entry_page_is_displayed_then_all_actions_are_displayed(
    entry_page: EntryPage,
):
    assert entry_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add entry ...",
        "Edit entry ...",
        "Delete entry",
        "Edit split times ...",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    entry_page: EntryPage, entry: None
):
    assert entry_page.actions.action("Reload").is_enabled()
    assert entry_page.actions.action("Import ...").is_enabled()
    assert entry_page.actions.action("Export ...").is_enabled()
    assert entry_page.actions.action("Add entry ...").is_enabled()
    assert entry_page.actions.action("Edit entry ...").is_disabled()
    assert entry_page.actions.action("Delete entry").is_disabled()
    assert entry_page.actions.action("Edit split times ...").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    entry_page: EntryPage, entry: None
):
    entry_page.table.select_row(i=2)

    assert entry_page.actions.action("Reload").is_enabled()
    assert entry_page.actions.action("Import ...").is_enabled()
    assert entry_page.actions.action("Export ...").is_enabled()
    assert entry_page.actions.action("Add entry ...").is_enabled()
    assert entry_page.actions.action("Edit entry ...").is_enabled()
    assert entry_page.actions.action("Delete entry").is_enabled()
    assert entry_page.actions.action("Edit split times ...").is_enabled()


def test_if_entry_page_is_selected_then_the_table_header_is_displayed(
    entry_page: EntryPage,
):
    assert entry_page.table.nr_of_columns() == 11
    assert entry_page.table.headers() == [
        "  NC  ",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]


def test_if_an_entry_is_added_with_required_data_then_an_additional_entry_is_displayed(
    entry_page: EntryPage, delete_entries: None
):
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
    entry_page: EntryPage, delete_entries: None
):
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
    entry_page: EntryPage, delete_entries: None
):
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


def test_if_an_already_registered_competitor_is_added_then_an_error_message_is_displayed(
    page: webdriver.Remote, entry_page: EntryPage, entry: None
):
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Annalena",
        last_name="Baerbock",
        class_name="Bahn A - Frauen",
        not_competing=True,
    )
    dialog.submit(wait_until_closed=False)
    alert = AlertWindow(page=page)
    assert alert.get_text() == "Competitor already registered for this event"
    alert.accept()
    dialog.cancel()


@pytest.mark.parametrize("gender", ["", "F", "M"])
def test_if_an_entry_is_added_you_can_choose_between_gender_unknown_and_female_and_male(
    gender: str, entry_page: EntryPage, delete_entries: None
):
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
    class_name: str, entry_page: EntryPage, delete_entries: None
):
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
    entry_page: EntryPage, entry: None
):
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


def test_if_an_entry_is_edited_then_the_changed_data_are_displayed(
    entry_page: EntryPage, entry: None
):
    entry_page.table.select_row(2)

    dialog = entry_page.actions.edit()
    dialog.check_values(
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
    dialog.enter_values(
        first_name="Anna Lena",
        last_name="Bärbock",
        gender="",
        year="1979",
        chip="1234567",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=True,
        start_time="",
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
        "Anna Lena",
        "Bärbock",
        "",
        "1979",
        "1234567",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


def test_if_a_row_is_double_clicked_the_edit_dialog_is_opened(
    entry_page: EntryPage, entry: None
):
    dialog = entry_page.table.double_click_row(2)
    dialog.check_values(
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
    dialog.enter_values(
        first_name="Anna Lena",
        last_name="Bärbock",
        gender="",
        year="1979",
        chip="1234567",
        club_name="",
        class_name="Bahn A - Frauen",
        not_competing=True,
        start_time="",
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
        "Anna Lena",
        "Bärbock",
        "",
        "1979",
        "1234567",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


def test_if_an_entry_is_deleted_then_the_entry_is_no_longer_displayed(
    entry_page: EntryPage, entry: None
):
    # add a second entry
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Nancy", last_name="Faeser", class_name="Bahn A - Frauen"
    )
    dialog.submit()
    assert entry_page.table.nr_of_rows() == 3

    # select entry
    entry_page.table.select_row(3)
    # delete entry
    entry_page.actions.delete().ok()

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
        "F",
        "1980",
        "7379879",
        "",
        "Bahn A - Frauen",
        "11:00:00",
        "",
        "",
    ]


def test_if_an_entry_is_deleted_then_no_entry_is_selected(
    entry_page: EntryPage, entry: None
):
    # add a second entry
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Nancy", last_name="Faeser", class_name="Bahn A - Frauen"
    )
    dialog.submit()

    # select entry
    entry_page.table.select_row(2)
    # delete entry
    entry_page.actions.delete().ok()

    assert entry_page.table.selected_row() is None


def test_if_deleting_an_entry_is_cancelled_then_the_entry_is_displayed_further(
    entry_page: EntryPage, entry: None
):
    # select entry
    entry_page.table.select_row(2)
    assert entry_page.table.selected_row() == 2

    # cancel deleting the entry
    entry_page.actions.delete().cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.row(i=1) == ["Entries  (1)"]
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


def test_if_several_entries_are_added_then_the_added_entries_are_displayed(
    entry_page: EntryPage, entry: None
):
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


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    entry_page: EntryPage, entry: None
):
    dialog = entry_page.actions.add()
    dialog.enter_values(
        first_name="Olaf",
        last_name="Scholz",
        gender="M",
        year="1959",
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

    try:
        entry_page.filter().set_text("1969")

        # check number of rows
        assert entry_page.table.nr_of_rows() == 2
        assert entry_page.table.nr_of_columns() == 11

        assert entry_page.table.row(i=1) == [
            "Entries  (3)",
        ]
        assert entry_page.table.row(i=2) == [
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
    finally:
        entry_page.filter().set_text("")

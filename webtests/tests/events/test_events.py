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

from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs
from webtests.tests.conftest import post


@pytest.fixture
def event_page(page: webdriver.Remote) -> EventPage:
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()
    return EventPage(page=page)


@pytest.fixture
def delete_events(event_page: EventPage):
    event_page.delete_events()


@pytest.fixture
def event(event_page, delete_events) -> None:
    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()
    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7


def test_all_actions_displayed(event_page: EventPage):
    assert event_page.actions.texts() == [
        "Reload",
        "Add event ...",
        "Edit event ...",
        "Delete event",
    ]


def test_some_actions_disabled_if_no_row_is_selected(event_page, event):
    assert event_page.actions.action("Reload").is_enabled()
    assert event_page.actions.action("Add event ...").is_enabled()
    assert event_page.actions.action("Edit event ...").is_disabled()
    assert event_page.actions.action("Delete event").is_disabled()


def test_all_actions_enabled_if_a_row_is_selected(event_page, event):
    event_page.table.select_row(i=1)

    assert event_page.actions.action("Reload").is_enabled()
    assert event_page.actions.action("Add event ...").is_enabled()
    assert event_page.actions.action("Edit event ...").is_enabled()
    assert event_page.actions.action("Delete event").is_enabled()


def test_table_header(event_page: EventPage):
    assert event_page.table.nr_of_columns() == 7
    assert event_page.table.headers() == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]


def test_add_event_with_required_data(event_page, delete_events):
    dialog = event_page.actions.add_event()
    dialog.check_values(
        name="",
        date="",
        key="",
        publish="no",
        series="",
        fields=[],
        streaming_address="",
        streaming_key="",
        streaming_enabled=False,
    )
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key=None,
        publish=None,
        series=None,
        fields=[],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "",
        "no",
        "",
        "",
        "",
    ]


def test_add_event_with_all_data(event_page, delete_events):
    dialog = event_page.actions.add_event()
    dialog.check_values(
        name="",
        date="",
        key="",
        publish="no",
        series="",
        fields=[],
        streaming_address="",
        streaming_key="",
        streaming_enabled=False,
    )
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_no_event_is_selected_and_a_new_event_is_added_then_no_event_is_selected(
    event_page, event
):
    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""

    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish="no",
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""


def test_adding_a_new_event_does_not_change_selected_event(event_page, event):
    event_page.table.select_row(i=1)
    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"

    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish="no",
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"


def test_edit_event(event_page, event):
    event_page.table.select_row(1)

    dialog = event_page.actions.edit_event()
    dialog.check_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.enter_values(
        name="Test-Lauf morgen",
        date="2023-12-29",
        key="local",
        publish="no",
        series="Serie 2",
        fields=["field"],
        streaming_address="myhost:8081",
        streaming_key="",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf morgen",
        "2023-12-29",
        "***",
        "no",
        "",
        "Serie 2",
        "field",
    ]


def test_if_an_event_is_deleted_no_event_is_selected(event_page, event):
    # select event
    event_page.table.select_row(1)
    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"

    # delete event
    event_page.actions.delete_event().ok()
    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""

    # check number of rows
    assert event_page.table.nr_of_rows() == 0
    assert event_page.table.nr_of_columns() == 7


def test_add_several_events(event_page, event):
    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish="no",
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish="no",
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 3
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf 1",
        "2023-12-29",
        "",
        "no",
        "",
        "Serie",
        "c, d",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf 2",
        "2023-12-29",
        "***",
        "no",
        "enabled",
        "Serie",
        "e, f",
    ]
    assert event_page.table.row(i=3) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(event_page, event):
    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish="no",
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    dialog = event_page.actions.add_event()
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish="no",
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 3
    assert event_page.table.nr_of_columns() == 7

    event_page.filter().set_text("heute")

    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_an_event_is_added_by_another_user_then_it_is_displayed_after_reload(
    event_page, event
):
    post(
        url="https://127.0.0.1:8080/event/add",
        data={
            "id": "",
            "name": "XXX Event",
            "date": "2024-05-17",
            "key": "",
            "publish": "no",
            "series": "",
            "fields": "",
            "streaming_address": "",
            "streaming_key": "",
            "streaming_enabled": "false",
        },
    )

    # check number of rows
    assert event_page.table.nr_of_rows() == 1
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]

    event_page.actions.reload()

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]
    assert event_page.table.row(i=2) == [
        "XXX Event",
        "2024-05-17",
        "",
        "no",
        "",
        "",
        "",
    ]

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
    Tabs(page=page).select(text="Events")
    return EventPage(page=page)


@pytest.fixture
def delete_events(event_page: EventPage) -> None:
    event_page.delete_events()


@pytest.fixture
def event(event_page: EventPage, delete_events: None) -> None:
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish=True,
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()
    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7


def test_if_event_page_is_displayed_then_all_actions_are_displayed(
    event_page: EventPage,
):
    assert event_page.actions.texts() == [
        "Reload",
        "Add event ...",
        "Edit event ...",
        "Delete event",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    event_page: EventPage, event: None
):
    assert event_page.actions.action("Reload").is_enabled()
    assert event_page.actions.action("Add event ...").is_enabled()
    assert event_page.actions.action("Edit event ...").is_disabled()
    assert event_page.actions.action("Delete event").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    event_page: EventPage, event: None
):
    event_page.table.select_row(i=2)

    assert event_page.actions.action("Reload").is_enabled()
    assert event_page.actions.action("Add event ...").is_enabled()
    assert event_page.actions.action("Edit event ...").is_enabled()
    assert event_page.actions.action("Delete event").is_enabled()


def test_if_event_page_is_selected_then_the_table_header_is_displayed(
    event_page: EventPage,
):
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


def test_if_an_event_is_added_with_required_data_then_an_additional_event_is_displayed(
    event_page: EventPage, delete_events: None
):
    dialog = event_page.actions.add()
    dialog.check_values(
        name="",
        date="",
        key="",
        publish=False,
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
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (1)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf heute",
        "2023-12-28",
        "",
        "",
        "",
        "",
        "",
    ]


def test_if_adding_an_event_is_cancelled_then_no_additional_event_is_displayed(
    event_page: EventPage, delete_events: None
):
    dialog = event_page.actions.add()
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
    dialog.cancel()

    # check number of rows
    assert event_page.table.nr_of_rows() == 0
    assert event_page.table.nr_of_columns() == 7


def test_if_an_event_is_added_with_all_data_then_an_additional_event_is_displayed(
    event_page: EventPage, delete_events: None
):
    dialog = event_page.actions.add()
    dialog.check_values(
        name="",
        date="",
        key="",
        publish=False,
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
        publish=True,
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (1)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_no_event_is_selected_and_a_new_event_is_added_then_no_event_is_selected(
    event_page: EventPage, event: None
):
    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""

    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish=False,
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""
    assert event_page.table.selected_row() is None


def test_if_a_new_event_is_added_then_the_selected_event_is_not_changed(
    event_page: EventPage, event: None
):
    event_page.table.select_row(i=2)
    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"
    assert event_page.table.selected_row() == 2

    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish=False,
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"
    row = event_page.table.selected_row()
    assert event_page.table.row(i=row) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_an_event_is_edited_then_the_changed_data_are_displayed(
    event_page: EventPage, event: None
):
    event_page.table.select_row(2)

    dialog = event_page.actions.edit()
    dialog.check_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish=True,
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
        publish=False,
        series="Serie 2",
        fields=["field"],
        streaming_address="myhost:8081",
        streaming_key="",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (1)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf morgen",
        "2023-12-29",
        "***",
        "",
        "",
        "Serie 2",
        "field",
    ]


def test_if_an_event_is_deleted_then_the_event_is_no_longer_displayed(
    event_page: EventPage, event: None
):
    # add a second event
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf morgen",
        date="2023-12-29",
        key="local",
        publish=False,
        series="Serie 2",
        fields=["field"],
        streaming_address="myhost:8081",
        streaming_key="",
        streaming_enabled=True,
    )
    dialog.submit()

    # select event
    event_page.table.select_row(3)
    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"

    # delete event
    event_page.actions.delete().ok()

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (1)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf morgen",
        "2023-12-29",
        "***",
        "",
        "",
        "Serie 2",
        "field",
    ]


def test_if_an_event_is_deleted_then_no_event_is_selected(
    event_page: EventPage, event: None
):
    # add a second event
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf morgen",
        date="2023-12-29",
        key="local",
        publish=False,
        series="Serie 2",
        fields=["field"],
        streaming_address="myhost:8081",
        streaming_key="",
        streaming_enabled=True,
    )
    dialog.submit()

    # select event
    event_page.table.select_row(3)
    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"

    # delete event
    event_page.actions.delete().ok()
    assert event_page.get_event_name() == ""
    assert event_page.get_event_date() == ""
    assert event_page.table.selected_row() is None


def test_if_deleting_an_event_is_cancelled_then_the_event_is_displayed_further(
    event_page: EventPage, event: None
):
    # select event
    event_page.table.select_row(2)
    assert event_page.table.selected_row() == 2

    # delete event
    event_page.actions.delete().cancel()

    assert event_page.get_event_name() == "Test-Lauf heute"
    assert event_page.get_event_date() == "2023-12-28"

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.row(i=1) == ["Events  (1)"]
    assert event_page.table.row(i=2) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_if_several_events_are_added_then_the_added_events_are_displayed(
    event_page: EventPage, event: None
):
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish=False,
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish=False,
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 4
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (3)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf 1",
        "2023-12-29",
        "",
        "",
        "",
        "Serie",
        "c, d",
    ]
    assert event_page.table.row(i=3) == [
        "Test-Lauf 2",
        "2023-12-29",
        "***",
        "",
        "enabled",
        "Serie",
        "e, f",
    ]
    assert event_page.table.row(i=4) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_events_are_displayed_ordered_by_date_descending(
    event_page: EventPage, event: None
):
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-27",
        key=None,
        publish=False,
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish=False,
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 4
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (3)",
    ]
    assert event_page.table.row(i=2) == [
        "Test-Lauf 2",
        "2023-12-29",
        "***",
        "",
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
    assert event_page.table.row(i=4) == [
        "Test-Lauf 1",
        "2023-12-27",
        "",
        "",
        "",
        "Serie",
        "c, d",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    event_page: EventPage, event: None
):
    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-29",
        key=None,
        publish=False,
        series="Serie",
        fields=["c", "d"],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

    dialog = event_page.actions.add()
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish=False,
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # check number of rows
    assert event_page.table.nr_of_rows() == 4
    assert event_page.table.nr_of_columns() == 7

    try:
        event_page.filter().set_text("heute")

        # check number of rows
        assert event_page.table.nr_of_rows() == 2
        assert event_page.table.nr_of_columns() == 7

        assert event_page.table.row(i=1) == [
            "Events  (3)",
        ]
        assert event_page.table.row(i=2) == [
            "Test-Lauf heute",
            "2023-12-28",
            "***",
            "yes",
            "enabled",
            "Serie",
            "a, b",
        ]
    finally:
        event_page.filter().set_text("")


def test_if_an_event_is_added_by_another_user_then_it_is_displayed_after_reload(
    event_page: EventPage, event: None
):
    post(
        url="https://127.0.0.1:8080/event/add",
        data={
            "id": "",
            "name": "XXX Event",
            "date": "2024-05-17",
            "key": "",
            "publish": "",
            "series": "",
            "fields": "",
            "streaming_address": "",
            "streaming_key": "",
            "streaming_enabled": "false",
        },
    )

    # check number of rows
    assert event_page.table.nr_of_rows() == 2
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (1)",
    ]
    assert event_page.table.row(i=2) == [
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
    assert event_page.table.nr_of_rows() == 3
    assert event_page.table.nr_of_columns() == 7

    assert event_page.table.row(i=1) == [
        "Events  (2)",
    ]
    assert event_page.table.row(i=2) == [
        "XXX Event",
        "2024-05-17",
        "",
        "",
        "",
        "",
        "",
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

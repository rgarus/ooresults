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


from webtests.pageobjects.events import EventPage


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

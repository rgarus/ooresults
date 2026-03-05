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

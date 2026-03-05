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


def test_if_a_row_is_double_clicked_the_edit_dialog_is_opened(
    event_page: EventPage, event: None
):
    dialog = event_page.table.double_click_row(2)
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

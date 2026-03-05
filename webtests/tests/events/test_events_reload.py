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
from webtests.tests.conftest import post


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

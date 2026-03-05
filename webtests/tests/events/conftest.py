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

from webtests.pageobjects.events import EventPage
from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.tabs import Tabs


@pytest.fixture
def event_page(main_page: MainPage) -> EventPage:
    Tabs(driver=main_page.driver).select(text="Events")
    return EventPage(driver=main_page.driver)


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

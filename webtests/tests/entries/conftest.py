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


from collections.abc import Iterator

import pytest

from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-12-28"


@pytest.fixture(scope="package")
def event(main_page: MainPage) -> Iterator[str]:
    event_page = main_page.goto_events()
    event_page.delete_events()
    dialog = event_page.actions.add()
    dialog.enter_values(
        name=EVENT_NAME,
        date=EVENT_DATE,
    )
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


@pytest.fixture(scope="package")
def add_classes(main_page: MainPage, event: str) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.delete_entries()
    class_page = main_page.goto_classes(event=event)
    class_page.delete_classes()
    dialog = class_page.actions.add()
    dialog.enter_values(name="Bahn A - Frauen")
    dialog.submit()
    dialog = class_page.actions.add()
    dialog.enter_values(name="Bahn A - Männer")
    dialog.submit()


@pytest.fixture
def delete_entries_and_competitors(main_page: MainPage, event: str) -> None:
    main_page.goto_entries(event=event).delete_entries()
    main_page.goto_competitors().delete_competitors()


@pytest.fixture
def entry(
    main_page: MainPage,
    event: str,
    add_classes: None,
    delete_entries_and_competitors: None,
) -> None:
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
    dialog.submit()
    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

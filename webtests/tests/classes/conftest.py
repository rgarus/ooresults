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


EVENT_NAME = "Test for Classes"
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
def add_courses(main_page: MainPage, event: str) -> None:
    course_page = main_page.goto_courses(event=event)
    course_page.delete_courses()
    dialog = course_page.actions.add()
    dialog.enter_values(name="Bahn A")
    dialog.submit()
    dialog = course_page.actions.add()
    dialog.enter_values(name="Bahn B")
    dialog.submit()


@pytest.fixture
def delete_classes(main_page: MainPage, event: str) -> None:
    main_page.goto_classes(event=event).delete_classes()


@pytest.fixture
def add_class(main_page: MainPage, event: str, delete_classes: None) -> None:
    class_page = main_page.goto_classes(event=event)
    dialog = class_page.actions.add()
    dialog.enter_values(
        name="Women Short",
        short_name="WS",
        course="",
        voided_legs="100-101",
        type="Net",
        use_start_control="Yes",
        apply_handicap=True,
        mass_start="12:30:00",
        time_limit="30:00",
        penalty_controls="400",
        penalty_time_limit="500",
    )
    dialog.submit()
    # check number of rows
    assert class_page.table.nr_of_rows() == 2
    assert class_page.table.nr_of_columns() == 11

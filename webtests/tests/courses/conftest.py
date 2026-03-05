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

from webtests.pageobjects.courses import CoursePage
from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Courses"
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


@pytest.fixture
def course_page(main_page: MainPage, event: str) -> CoursePage:
    return main_page.goto_courses(event=event)


@pytest.fixture
def delete_courses(main_page: MainPage, event: str) -> None:
    main_page.goto_courses(event=event).delete_courses()


@pytest.fixture
def course(main_page: MainPage, event: str, delete_courses: None) -> None:
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.add()
    dialog.enter_values(
        name="Bahn B",
        length="4500",
        climb="60",
        controls="122-123-124-125-121",
    )
    dialog.submit()
    # check number of rows
    assert course_page.table.nr_of_rows() == 2
    assert course_page.table.nr_of_columns() == 4

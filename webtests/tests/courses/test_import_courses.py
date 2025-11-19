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


import pathlib
import tempfile

import pytest
from selenium import webdriver

from webtests.pageobjects.courses import CoursePage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs


EVENT_NAME = "Test for Courses"
EVENT_DATE = "2023-12-28"


@pytest.fixture(scope="module")
def select_event(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()
    dialog = event_page.actions.add()
    dialog.enter_values(
        name=EVENT_NAME,
        date=EVENT_DATE,
    )
    dialog.submit()
    event_page.table.select_row(2)
    yield
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()


@pytest.fixture
def course_page(page: webdriver.Remote, select_event: None) -> CoursePage:
    Tabs(page=page).select(text="Courses")
    return CoursePage(page=page)


@pytest.fixture
def delete_courses(course_page: CoursePage) -> None:
    course_page.delete_courses()


def test_import_courses(course_page: CoursePage, delete_courses: None):
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
  <RaceCourseData>
    <Course>
      <Name>Bahn A</Name>
      <Length>4500</Length>
      <Climb>90</Climb>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>121</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>124</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>122</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>123</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
    <Course>
      <Name>Bahn B</Name>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>131</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>132</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
  </RaceCourseData>
</CourseData>
"""
    dialog = course_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "CourseData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_(path=path)

    # check number of rows
    assert course_page.table.nr_of_rows() == 3
    assert course_page.table.nr_of_columns() == 4

    assert course_page.table.row(i=1) == [
        "Courses  (2)",
    ]
    assert course_page.table.row(i=2) == [
        "Bahn A",
        "4500",
        "90",
        "121 - 124 - 122 - 123",
    ]
    assert course_page.table.row(i=3) == [
        "Bahn B",
        "",
        "",
        "131 - 132",
    ]

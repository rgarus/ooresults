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

from webtests.controls.alert_window import AlertWindow
from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Courses"
EVENT_DATE = "2023-12-28"


def test_import_courses(main_page: MainPage, event: str, delete_courses: None) -> None:
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
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "CourseData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path)

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


def test_if_import_course_data_with_xml_errors_then_an_error_message_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
) -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Even>
</CourseData>
"""
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "CourseData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, error_dialog=True)

    # check error message
    alert = AlertWindow(driver=course_page.driver)
    assert (
        alert.get_text()
        == "Opening and ending tag mismatch: "
        + "Event line 3 and Even, line 8, column 10 (<string>, line 8)"
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert course_page.table.nr_of_rows() == 0


def test_if_import_course_data_with_schema_errors_then_an_error_message_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
) -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
</CourseData>
"""
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "CourseData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, error_dialog=True)

    # check error message
    alert = AlertWindow(driver=course_page.driver)
    assert (
        alert.get_text()
        == "<string>:2:0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT: "
        + "Element '{http://www.orienteering.org/datastandard/3.0}CourseData': "
        + "Missing child element(s). "
        + "Expected is ( {http://www.orienteering.org/datastandard/3.0}RaceCourseData )."
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert course_page.table.nr_of_rows() == 0


def test_if_import_course_data_but_root_tag_is_not_class_list_then_an_error_message_is_displayed(
    main_page: MainPage, event: str, delete_courses: None
) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    course_page = main_page.goto_courses(event=event)
    dialog = course_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "CourseData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, error_dialog=True)

    # check error message
    alert = AlertWindow(driver=course_page.driver)
    assert (
        alert.get_text()
        == "Root element is {http://www.orienteering.org/datastandard/3.0}ResultList "
        + "but should be CourseData"
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert course_page.table.nr_of_rows() == 0

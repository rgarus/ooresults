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


import datetime

from ooresults.plugins import iof_course_data
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.course_type import CourseType
from ooresults.repo.event_type import EventType


def test_import_course_data():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <RaceCourseData>
    <Course>
      <Name>Bahn A</Name>
      <Length>4800</Length>
      <Climb>120</Climb>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>102</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>103</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>104</Control>
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
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>105</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>106</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>104</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
  </RaceCourseData>
</CourseData>
"""
    event, courses, class_course = iof_course_data.parse_course_data(
        bytes(content, encoding="utf-8")
    )
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
    }
    assert courses == [
        {
            "name": "Bahn A",
            "length": 4800,
            "climb": 120,
            "controls": ["101", "102", "103", "104"],
        },
        {
            "name": "Bahn B",
            "length": None,
            "climb": None,
            "controls": ["101", "105", "106", "104"],
        },
    ]
    assert class_course == []


def test_import_course_data_with_class_assignment():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <RaceCourseData>
    <Course>
      <Name>Bahn A</Name>
      <Length>4800</Length>
      <Climb>120</Climb>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>102</Control>
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
        <Control>104</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
    <ClassCourseAssignment>
      <ClassName>Elite Men</ClassName>
      <CourseName>Bahn B</CourseName>
    </ClassCourseAssignment>
    <ClassCourseAssignment>
      <ClassName>Elite Woman</ClassName>
      <CourseName>Bahn A</CourseName>
    </ClassCourseAssignment>
    <ClassCourseAssignment>
      <ClassName>Beginners</ClassName>
    </ClassCourseAssignment>
  </RaceCourseData>
</CourseData>
"""
    event, courses, class_course = iof_course_data.parse_course_data(
        bytes(content, encoding="utf-8")
    )
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
    }
    assert courses == [
        {
            "name": "Bahn A",
            "length": 4800,
            "climb": 120,
            "controls": ["101", "102"],
        },
        {
            "name": "Bahn B",
            "length": None,
            "climb": None,
            "controls": ["104"],
        },
    ]
    assert class_course == [
        {
            "class_name": "Elite Men",
            "course_name": "Bahn B",
        },
        {
            "class_name": "Elite Woman",
            "course_name": "Bahn A",
        },
        {
            "class_name": "Beginners",
            "course_name": None,
        },
    ]


def test_export_course_data():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <RaceCourseData>
    <Course>
      <Name>Bahn A</Name>
      <Length>4800</Length>
      <Climb>120</Climb>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>102</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>103</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>104</Control>
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
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>105</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>106</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>104</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
  </RaceCourseData>
</CourseData>
"""
    document = iof_course_data.create_course_data(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=datetime.date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            CourseType(
                id=1,
                event_id=1,
                name="Bahn A",
                length=4800,
                climb=120,
                controls=["101", "102", "103", "104"],
            ),
            CourseType(
                id=2,
                event_id=1,
                name="Bahn B",
                length=None,
                climb=None,
                controls=["101", "105", "106", "104"],
            ),
        ],
        [],
    )
    assert document == bytes(content, encoding="utf-8")


def test_export_course_data_with_class_assignment():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CourseData xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <RaceCourseData>
    <Course>
      <Name>Bahn A</Name>
      <Length>4800</Length>
      <Climb>120</Climb>
      <CourseControl type="Start">
        <Control>S1</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>101</Control>
      </CourseControl>
      <CourseControl type="Control">
        <Control>102</Control>
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
        <Control>104</Control>
      </CourseControl>
      <CourseControl type="Finish">
        <Control>F1</Control>
      </CourseControl>
    </Course>
    <ClassCourseAssignment>
      <ClassName>Elite Men</ClassName>
      <CourseName>Bahn B</CourseName>
    </ClassCourseAssignment>
    <ClassCourseAssignment>
      <ClassName>Elite Woman</ClassName>
      <CourseName>Bahn A</CourseName>
    </ClassCourseAssignment>
    <ClassCourseAssignment>
      <ClassName>Beginners</ClassName>
    </ClassCourseAssignment>
  </RaceCourseData>
</CourseData>
"""
    document = iof_course_data.create_course_data(
        EventType(
            id=1,
            name="1. O-Cup 2020",
            date=datetime.date(year=2020, month=2, day=9),
            key=None,
            publish=False,
            series=None,
            fields=[],
        ),
        [
            CourseType(
                id=1,
                event_id=1,
                name="Bahn A",
                length=4800,
                climb=120,
                controls=["101", "102"],
            ),
            CourseType(
                id=2,
                event_id=1,
                name="Bahn B",
                length=None,
                climb=None,
                controls=["104"],
            ),
        ],
        [
            ClassInfoType(
                id=1,
                name="Elite Men",
                short_name=None,
                course_id=2,
                course_name="Bahn B",
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=2,
                name="Elite Woman",
                short_name=None,
                course_id=1,
                course_name="Bahn A",
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=3,
                name="Beginners",
                short_name=None,
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
        ],
    )
    assert document == bytes(content, encoding="utf-8")

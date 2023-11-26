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
from typing import List
from typing import Dict
from typing import Tuple

import iso8601
from lxml import etree
from lxml.builder import ElementMaker

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.course_type import CourseType
from ooresults.repo.event_type import EventType


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


iof_namespace = "http://www.orienteering.org/datastandard/3.0"
namespaces = {None: iof_namespace}


def create_course_data(
    event: EventType, courses: List[CourseType], classes: List[ClassInfoType]
) -> bytes:
    E = ElementMaker(namespace=iof_namespace, nsmap=namespaces)

    COURSEDATA = E.CourseData
    EVENT = E.Event
    NAME = E.Name
    STARTTIME = E.StartTime
    DATE = E.Date
    RACECOURSEDATA = E.RaceCourseData
    COURSE = E.Course
    LENGTH = E.Length
    CLIMB = E.Climb
    COURSECONTROL = E.CourseControl
    CONTROL = E.Control
    CLASSCOURSEASSIGNMENT = E.ClassCourseAssignment
    CLASSNAME = E.ClassName
    COURSENAME = E.CourseName

    root = COURSEDATA(
        iofVersion="3.0",
        creator="ooresults (https://pypi.org/project/ooresults)",
    )

    e_event = EVENT()
    e_event.append(NAME(event.name))
    e_event.append(STARTTIME(DATE(event.date.isoformat())))
    root.append(e_event)

    race_course_data = RACECOURSEDATA()
    for c in courses:
        course = COURSE()
        course.append(NAME(c.name))

        if c.length is not None:
            course.append(LENGTH(str(round(c.length))))
        if c.climb is not None:
            course.append(CLIMB(str(round(c.climb))))

        cc = COURSECONTROL(CONTROL("S1"))
        cc.set("type", "Start")
        course.append(cc)

        for control in c.controls:
            cc = COURSECONTROL(CONTROL(control))
            cc.set("type", "Control")
            course.append(cc)

        cc = COURSECONTROL(CONTROL("F1"))
        cc.set("type", "Finish")
        course.append(cc)

        race_course_data.append(course)

    for c in classes:
        class_course_assignment = CLASSCOURSEASSIGNMENT()
        class_course_assignment.append(CLASSNAME(c.name))

        if c.course_name:
            class_course_assignment.append(COURSENAME(c.course_name))

        race_course_data.append(class_course_assignment)

    root.append(race_course_data)

    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    return etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )


def parse_course_data(content: bytes) -> Tuple[Dict, List[Dict], List[Dict]]:
    # Event: Dict of {'name': str, 'date': Optional[str]}
    # Course: Dict of {'name': str, 'length': Optional[float], 'climb': Optional[float], 'controls': List[str]}
    # ClassCourseAssignment: Dict of {'class_name': str, 'course_name': Optional[str]}

    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + iof_namespace + "}CourseData":
        raise RuntimeError("Root element is " + root.tag + " but should be CourseData")

    event = {}
    event["name"] = root.find("Event/Name", namespaces=namespaces).text
    date = root.find("Event/StartTime/Date", namespaces=namespaces)
    if date is not None:
        event["date"] = iso8601.parse_date(date.text).date()

    result = []
    race_course_data_list = root.findall("RaceCourseData", namespaces=namespaces)

    course_list = race_course_data_list[0].findall("Course", namespaces=namespaces)
    courses = []
    for course in course_list:
        c = {"name": "", "length": None, "climb": None, "controls": []}
        c["name"] = course.find("Name", namespaces=namespaces).text

        length = course.find("Length", namespaces=namespaces)
        if length is not None:
            c["length"] = float(length.text)
        climb = course.find("Climb", namespaces=namespaces)
        if climb is not None:
            c["climb"] = float(climb.text)

        course_control_list = course.findall("CourseControl", namespaces=namespaces)
        for course_control in course_control_list:
            control_type = course_control.get("type", default="Control")
            if control_type == "Control":
                control_list = course_control.findall("Control", namespaces=namespaces)
                c["controls"].append(control_list[0].text)

        courses.append(c)

    class_course_assignment_list = race_course_data_list[0].findall(
        "ClassCourseAssignment", namespaces=namespaces
    )
    class_course_assignments = []
    for assignment in class_course_assignment_list:
        a = {
            "class_name": "",
            "course_name": None,
        }
        a["class_name"] = assignment.find("ClassName", namespaces=namespaces).text
        course_name = assignment.find("CourseName", namespaces=namespaces)
        if course_name is not None:
            a["course_name"] = course_name.text

        class_course_assignments.append(a)

    return event, courses, class_course_assignments

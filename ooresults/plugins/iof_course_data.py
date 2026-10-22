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

import iso8601
from lxml import etree
from lxml.builder import ElementMaker

from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.event_type import EventType
from ooresults.plugins.import_types.course_dict import ClassCourseAssignmentDict
from ooresults.plugins.import_types.course_dict import CourseDict
from ooresults.plugins.import_types.event_dict import EventDict


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


IOF_NAMESPACE = "http://www.orienteering.org/datastandard/3.0"
NSMAP = {None: IOF_NAMESPACE}


def create_course_data(
    event: EventType, courses: list[CourseType], classes: list[ClassInfoType]
) -> bytes:
    E = ElementMaker(namespace=IOF_NAMESPACE, nsmap=NSMAP)

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


def parse_course_data(
    content: bytes,
) -> tuple[EventDict, list[CourseDict], list[ClassCourseAssignmentDict]]:
    NS = {"": IOF_NAMESPACE}

    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + IOF_NAMESPACE + "}CourseData":
        raise RuntimeError(f"Root element is {str(root.tag)} but should be CourseData")

    event = EventDict(name="", date=None)
    name = root.find("Event/Name", namespaces=NS)
    if name is not None and (text := name.text):
        event["name"] = text
    else:
        raise RuntimeError("Event/Name missing or empty")

    date = root.find("Event/StartTime/Date", namespaces=NS)
    if date is not None and (text := date.text):
        event["date"] = iso8601.parse_date(text).date()

    courses: list[CourseDict] = []
    race_course_data_list = root.findall("RaceCourseData", namespaces=NS)

    course_list = race_course_data_list[0].findall("Course", namespaces=NS)
    for course in course_list:
        c = CourseDict(name="", length=None, climb=None, controls=[])

        name = course.find("Name", namespaces=NS)
        if name is not None and (text := name.text):
            c["name"] = text
        else:
            raise RuntimeError("Course/Name missing or empty")

        length = course.find("Length", namespaces=NS)
        if length is not None and (text := length.text):
            c["length"] = float(text)
        climb = course.find("Climb", namespaces=NS)
        if climb is not None and (text := climb.text):
            c["climb"] = float(text)

        course_control_list = course.findall("CourseControl", namespaces=NS)
        for course_control in course_control_list:
            control_type = course_control.get("type", default="Control")
            if control_type == "Control":
                control_list = course_control.findall("Control", namespaces=NS)
                if control_list and (text := control_list[0].text) is not None:
                    c["controls"].append(text)

        courses.append(c)

    class_course_assignments: list[ClassCourseAssignmentDict] = []
    class_course_assignment_list = race_course_data_list[0].findall(
        "ClassCourseAssignment", namespaces=NS
    )
    for assignment in class_course_assignment_list:
        a = ClassCourseAssignmentDict(class_name="", course_name=None)

        class_name = assignment.find("ClassName", namespaces=NS)
        if class_name is not None and (text := class_name.text):
            a["class_name"] = text
        else:
            raise RuntimeError("ClassName missing or empty")

        course_name = assignment.find("CourseName", namespaces=NS)
        if course_name is not None and (text := course_name.text):
            a["course_name"] = text

        class_course_assignments.append(a)

    return event, courses, class_course_assignments

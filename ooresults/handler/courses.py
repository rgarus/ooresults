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


import io

import bottle

from ooresults import model
from ooresults.plugins import iof_course_data
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import CourseUsedError
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import render


"""
Handler for the course routes.

/course/update
/course/import
/course/export
/course/add
/course/fill_edit_form
/course/delete
"""


def update(event_id: int):
    courses = model.courses.get_courses(event_id=event_id)
    try:
        event = model.events.get_event(id=event_id)
        return render.courses_table(event=event, courses=courses)
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")


@bottle.post("/course/update")
def post_update():
    """Update data"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    return update(event_id=event_id)


@bottle.post("/course/import")
def post_import():
    """Import entries"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.cou_import == "cou.import.1":
            with io.BytesIO() as buffer:
                bottle.request.files.browse1.save(buffer)
                _, courses, class_course = iof_course_data.parse_course_data(
                    content=buffer.getvalue(),
                )
            model.courses.import_courses(
                event_id=event_id, courses=courses, class_course=class_course
            )

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except Exception as e:
        return bottle.HTTPResponse(status=409, body=str(e))

    return update(event_id)


@bottle.post("/course/export")
def post_export():
    """Export entries"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.cou_export == "cou.export.1":
            event = model.events.get_event(id=event_id)
            courses = model.courses.get_courses(event_id=event_id)
            classes = model.classes.get_classes(event_id=event_id)
            content = iof_course_data.create_course_data(event, courses, classes)

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")

    return content


@bottle.post("/course/add")
def post_add():
    """Add or edit entry"""
    data = bottle.request.forms
    print(data)
    event_id = int(data.event_id) if data.event_id != "" else -1
    length = int(data.length) if data.length != "" else None
    climb = int(data.climb) if data.climb != "" else None
    controls = data.controls.split("-") if data.controls != "" else []
    controls = [c.strip() for c in controls]
    try:
        if data.id == "":
            model.courses.add_course(
                event_id=event_id,
                name=data.name,
                length=length,
                climb=climb,
                controls=controls,
            )
        else:
            model.courses.update_course(
                id=int(data.id),
                event_id=event_id,
                name=data.name,
                length=length,
                climb=climb,
                controls=controls,
            )

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Course deleted")

    return update(event_id)


@bottle.post("/course/delete")
def post_delete():
    """Delete entry"""
    data = bottle.request.forms
    print(data)
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        model.courses.delete_course(id=int(data.id))
        return update(event_id)
    except CourseUsedError:
        return bottle.HTTPResponse(status=409, body="Course used in classes")


@bottle.post("/course/fill_edit_form")
def post_fill_edit_form():
    """Query data to fill add or edit form"""
    data = bottle.request.forms
    try:
        if data.id == "":
            course = None
        else:
            course = model.courses.get_course(id=int(data.id))
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Course deleted")

    return render.add_course(course=course)

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


import logging
import pathlib

import web
from web.utils import Storage

from ooresults.handler import model
from ooresults.repo.repo import CourseUsedError
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import ConstraintError
from ooresults.plugins import iof_course_data
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


def update(event_id: int):
    courses_list = model.get_courses(event_id=event_id)
    event = list(model.get_event(event_id))
    if event == []:
        return render.courses_table({}, courses_list)
    else:
        return render.courses_table(event[0], courses_list)


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        return update(event_id)


class Import:
    def POST(self):
        """Import entries"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            event = {}
            if data.cou_import == "cou.import.1":
                event, courses, class_course = iof_course_data.parse_course_data(
                    data.browse1
                )
                model.import_courses(
                    event_id=event_id, courses=courses, class_course=class_course
                )

        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except Exception as e:
            raise web.Conflict(str(e))

        return update(event_id)


class Export:
    def POST(self):
        """Export entries"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.cou_export == "cou.export.1":
                event = model.get_event(id=event_id)
                courses = model.get_courses(event_id=event_id)
                classes = model.get_classes(event_id=event_id)
                content = iof_course_data.create_course_data(event[0], courses, classes)

        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content


class Add:
    def POST(self):
        """Add or edit entry"""
        data = web.input()
        print(data)
        event_id = int(data.event_id) if data.event_id != "" else -1
        length = int(data.length) if data.length != "" else None
        climb = int(data.climb) if data.climb != "" else None
        controls = data.controls.split("-") if data.controls != "" else []
        controls = [c.strip() for c in controls]
        try:
            if data.id == "":
                model.add_course(
                    event_id=event_id,
                    name=data.name,
                    length=length,
                    climb=climb,
                    controls=controls,
                )
            else:
                model.update_course(
                    id=int(data.id),
                    event_id=event_id,
                    name=data.name,
                    length=length,
                    climb=climb,
                    controls=controls,
                )

        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except ConstraintError as e:
            raise web.conflict(str(e))
        except KeyError:
            raise web.conflict("Course deleted")
        except:
            logging.exception("Internal server error")
            raise

        return update(event_id)


class Delete:
    def POST(self):
        """Delete entry"""
        data = web.input()
        print(data)
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            model.delete_course(id=int(data.id))
            return update(event_id)
        except CourseUsedError:
            raise web.conflict("Course used in classes")
        except:
            logging.exception("Internal server error")
            raise


class FillEditForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        try:
            if data.id == "":
                course = Storage(
                    {
                        "id": "",
                        "name": "",
                        "length": None,
                        "climb": None,
                        "controls": "",
                    }
                )
            else:
                course = model.get_course(id=int(data.id))[0]
        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except KeyError:
            raise web.conflict("Course deleted")
        except:
            logging.exception("Internal server error")
            raise

        return render.add_course(course)

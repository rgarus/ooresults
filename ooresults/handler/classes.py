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
import pathlib
import logging
from typing import Optional

import tzlocal
import web
from web.utils import Storage

from ooresults.handler import model
from ooresults.repo.repo import ClassUsedError
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import ConstraintError
from ooresults.repo.class_params import ClassParams
from ooresults.plugins import iof_class_list
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


def update(event_id: int):
    classes_list = model.get_classes(event_id=event_id)
    event = list(model.get_event(event_id))
    if event == []:
        return render.classes_table({}, classes_list)
    else:
        return render.classes_table(event[0], classes_list)


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        return update(event_id)


class Import:
    def POST(self):
        """Import classes"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.cls_import == "cls.import.1":
                classes = iof_class_list.parse_class_list(data.browse1)
                model.import_classes(event_id=event_id, classes=classes)

        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except Exception as e:
            raise web.Conflict(str(e))

        return update(event_id)


class Export:
    def POST(self):
        """Export classes"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.cls_export == "cls.export.1":
                classes = model.get_classes(event_id=event_id)
                content = iof_class_list.create_class_list(classes)

        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content


class Add:
    def parse_start_time(
        self, item: str, event_date: datetime.date
    ) -> Optional[datetime.datetime]:
        if item != "":
            format = "%H:%M:%S" if item.count(":") == 2 else "%M:%S"
            tz = tzlocal.get_localzone()
            dt = datetime.datetime.combine(
                date=event_date,
                time=datetime.datetime.strptime(item, format).time(),
                tzinfo=tz,
            )
            print(">>> ", dt)
            return dt
        else:
            return None

    def POST(self):
        """Add or edit entry"""
        data = web.input()
        print(data)
        event_id = int(data.event_id) if data.event_id != "" else -1
        event = model.get_event(id=event_id)[0]

        params = ClassParams()
        params.otype = data.get("type", "standard")
        params.using_start_control = data.get("startControl", "if_punched")
        params.mass_start = self.parse_start_time(data.massStart, event.date)
        params.apply_handicap_rule = data.get("handicap", "0") == "1"
        if data.get("timeLimit", "") != "":
            m, _, s = data["timeLimit"].partition(":")
            params.time_limit = 60 * int(m) + int(s)
        else:
            params.time_limit = None
        params.penalty_controls = (
            int(data.get("penaltyControls", ""))
            if data.get("penaltyControls", "") != ""
            else None
        )
        params.penalty_overtime = (
            int(data.get("penaltyOvertime", ""))
            if data.get("penaltyOvertime", "") != ""
            else None
        )

        voided_legs = (
            data.get("voided_legs", "").split(",")
            if data.get("voided_legs", "") != ""
            else []
        )
        for v in voided_legs:
            # there should be two controls separated by '-'
            controls = v.split("-")
            if len(controls) == 2:
                if (controls[0].strip(), controls[1].strip()) not in params.voided_legs:
                    params.voided_legs.append(
                        (controls[0].strip(), controls[1].strip())
                    )
            else:
                raise web.conflict(
                    'Format of voided legs incorrect, use "c1-c2, c3-c4, ..."'
                )

        try:
            course_id = int(data.course) if data.course != "" else None
            if data.id == "":
                model.add_class(
                    event_id=event_id,
                    name=data.name,
                    short_name=data.short_name if data.short_name != "" else None,
                    course_id=course_id,
                    params=params,
                )

            else:
                model.update_class(
                    id=int(data.id),
                    event_id=event_id,
                    name=data.name,
                    short_name=data.short_name if data.short_name != "" else None,
                    course_id=int(data.course) if data.course != "" else None,
                    params=params,
                )

        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except ConstraintError as e:
            raise web.conflict(str(e))
        except KeyError:
            raise web.conflict("Class deleted")
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
            model.delete_class(id=int(data.id))
            return update(event_id)

        except ClassUsedError:
            raise web.conflict("Class used in entries")
        except:
            logging.exception("Internal server error")
            raise


class FillEditForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.id == "":
                class_ = Storage(
                    {
                        "id": "",
                        "name": "",
                        "short_name": None,
                        "course_id": None,
                        "params": ClassParams(),
                    }
                )
            else:
                class_ = model.get_class(id=int(data.id))[0]

        except EventNotFoundError:
            raise web.conflict("No event selected or event deleted")
        except KeyError:
            raise web.conflict("Class deleted")
        except:
            logging.exception("Internal server error")
            raise

        courses = model.get_courses(event_id=event_id)
        return render.add_class(class_, courses)

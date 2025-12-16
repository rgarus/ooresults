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
import io
from typing import Optional

import bottle
import tzlocal

from ooresults import model
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_params import VoidedLeg
from ooresults.plugins import iof_class_list
from ooresults.repo.repo import ClassUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import render


"""
Handler for the class routes.

/class/update
/class/import
/class/export
/class/add
/class/fill_edit_form
/class/delete
"""


def update(event_id: int):
    classes = model.classes.get_classes(event_id=event_id)
    try:
        event = model.events.get_event(id=event_id)
        return render.classes_table(event=event, classes=classes)
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")


@bottle.post("/class/update")
def post_update():
    """Update data."""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    return update(event_id=event_id)


@bottle.post("/class/import")
def post_import():
    """Import classes."""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.cls_import == "cls.import.1":
            with io.BytesIO() as buffer:
                bottle.request.files.browse1.save(buffer)
                classes = iof_class_list.parse_class_list(content=buffer.getvalue())
            model.classes.import_classes(event_id=event_id, classes=classes)

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except Exception as e:
        return bottle.HTTPResponse(status=409, body=str(e))

    return update(event_id)


@bottle.post("/class/export")
def post_export():
    """Export classes."""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.cls_export == "cls.export.1":
            classes = model.classes.get_classes(event_id=event_id)
            content = iof_class_list.create_class_list(classes)

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")

    return content


def parse_start_time(
    item: str, event_date: datetime.date
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


@bottle.post("/class/add")
def post_add():
    """Add or edit class."""
    data = bottle.request.forms
    print(dict(data))
    event_id = int(data.event_id) if data.event_id != "" else -1

    params = ClassParams()
    params.otype = data.get("type", "standard")
    params.using_start_control = data.get("startControl", "if_punched")
    params.apply_handicap_rule = data.get("handicap", "") == "true"
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
            voided_leg = VoidedLeg(
                control_1=controls[0].strip(),
                control_2=controls[1].strip(),
            )
            if voided_leg not in params.voided_legs:
                params.voided_legs.append(voided_leg)

        else:
            return bottle.HTTPResponse(
                status=409,
                body='Format of voided legs incorrect, use "c1-c2, c3-c4, ..."',
            )

    try:
        event = model.events.get_event(id=event_id)

        params.mass_start = parse_start_time(data.massStart, event.date)
        course_id = int(data.course_id) if data.course_id != "" else None
        if data.id == "":
            model.classes.add_class(
                event_id=event_id,
                name=data.name,
                short_name=data.short_name if data.short_name != "" else None,
                course_id=course_id,
                params=params,
            )

        else:
            model.classes.update_class(
                id=int(data.id),
                event_id=event_id,
                name=data.name,
                short_name=data.short_name if data.short_name != "" else None,
                course_id=course_id,
                params=params,
            )

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Class deleted")

    return update(event_id)


@bottle.post("/class/delete")
def post_delete():
    """Delete class."""
    data = bottle.request.forms
    print(dict(data))
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        model.classes.delete_class(id=int(data.id))
        return update(event_id)

    except ClassUsedError:
        return bottle.HTTPResponse(status=409, body="Class used in entries")


@bottle.post("/class/fill_edit_form")
def post_fill_edit_form():
    """Query data to fill add or edit form."""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.id == "":
            class_ = None
        else:
            class_ = model.classes.get_class(id=int(data.id))

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Class deleted")

    courses = model.courses.get_courses(event_id=event_id)
    return render.add_class(class_=class_, courses=courses)

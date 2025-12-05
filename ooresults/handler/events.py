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

import bottle

from ooresults import model
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import render


"""
Handler for the event routes.

/event/update
/event/add
/event/fill_edit_form
/event/delete
"""


def update():
    return render.events_table(events=model.events.get_events())


@bottle.post("/event/update")
def post_update():
    """Update data"""
    return update()


@bottle.post("/event/add")
def post_add():
    """Add or edit entry"""
    data = bottle.request.forms
    print(data)
    try:
        fields = data.fields.split(",") if data.fields != "" else []
        fields = [f.strip() for f in fields]
        streaming_enabled = None
        if data.streaming_address and data.streaming_key:
            streaming_enabled = (
                "streaming_enabled" in data and data.streaming_enabled == "true"
            )

        if data.id == "":
            model.events.add_event(
                name=data.name,
                date=datetime.datetime.strptime(data.date, "%Y-%m-%d").date(),
                key=data.key if data.key != "" else None,
                publish="publish" in data and data.publish == "true",
                series=data.series if data.series != "" else None,
                fields=fields,
                streaming_address=data.streaming_address,
                streaming_key=data.streaming_key,
                streaming_enabled=streaming_enabled,
            )
        else:
            model.events.update_event(
                id=int(data.id),
                name=data.name,
                date=datetime.datetime.strptime(data.date, "%Y-%m-%d").date(),
                key=data.key if data.key != "" else None,
                publish="publish" in data and data.publish == "true",
                series=data.series if data.series != "" else None,
                fields=fields,
                streaming_address=data.streaming_address,
                streaming_key=data.streaming_key,
                streaming_enabled=streaming_enabled,
            )
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))

    return update()


@bottle.post("/event/delete")
def post_delete():
    """Delete entry"""
    data = bottle.request.forms
    model.events.delete_event(int(data.id))
    return update()


@bottle.post("/event/fill_edit_form")
def post_fill_edit_form():
    """Query data to fill add or edit form"""
    data = bottle.request.forms
    try:
        if data.id == "":
            event = None
        else:
            event = model.events.get_event(id=int(data.id))

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")

    return render.add_event(event=event)

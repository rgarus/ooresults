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


import bottle

from ooresults import model
from ooresults.utils import render


"""
Handler for the si1 routes.

/si1
"""


@bottle.get("/si1")
def get_si1():
    event_id = None
    key = None
    view = 0

    data = bottle.request.params
    if "view" in data and data.view in ["0", "1"]:
        view = int(data.view)

    try:
        for event in model.events.get_events():
            if event.key:
                event_id = event.id
                key = event.key
                break
    except Exception:
        pass

    return render.si1_page(event_id=event_id, key=key, view=view)

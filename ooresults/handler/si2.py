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
Handler for the si2 routes.

/si2
"""


@bottle.get("/si2")
def get_si2():
    event_id = None
    key = None
    data = bottle.request.params

    try:
        for event in model.events.get_events():
            if str(event.id) == data.id:
                event_id = event.id
                key = event.key
    except Exception:
        pass

    return render.si2_page(event_id=event_id, key=key)

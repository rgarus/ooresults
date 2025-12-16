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
from ooresults.repo.repo import ClubUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.utils import render


"""
Handler for the club routes.

/club/update
/club/add
/club/fill_edit_form
/club/delete
"""


@bottle.post("/club/update")
def post_update():
    """Update data."""
    return render.clubs_table(clubs=model.clubs.get_clubs())


@bottle.post("/club/add")
def post_add():
    """Add or edit club."""
    data = bottle.request.forms
    print(dict(data))
    try:
        if data.id == "":
            model.clubs.add_club(data.name)
        else:
            model.clubs.update_club(int(data.id), data.name)
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Club deleted")

    return render.clubs_table(clubs=model.clubs.get_clubs())


@bottle.post("/club/delete")
def post_delete():
    """Delete club."""
    data = bottle.request.forms
    print(dict(data))
    try:
        model.clubs.delete_club(int(data.id))
        return render.clubs_table(clubs=model.clubs.get_clubs())
    except ClubUsedError:
        return bottle.HTTPResponse(
            status=409, body="Club used in competitors or entries"
        )


@bottle.post("/club/fill_edit_form")
def post_fill_edit_form():
    """Query data to fill add or edit form."""
    data = bottle.request.forms
    try:
        if data.id == "":
            club = None
        else:
            club = model.clubs.get_club(int(data.id))
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Club deleted")

    return render.add_club(club=club)

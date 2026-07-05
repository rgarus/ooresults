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
from collections import defaultdict
from typing import Optional

import bottle

from ooresults import model
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.plugins import iof_competitor_list
from ooresults.repo.repo import CompetitorUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.utils import render


"""
Handler for the competitor routes.

/competitor/update
/competitor/import
/competitor/export
/competitor/add
/competitor/fill_edit_form
/competitor/delete
"""


def update(view: str = "Competitors") -> str:
    def to_str(item: Optional[str]) -> str:
        return item if item is not None else ""

    competitors = model.competitors.get_competitors()

    view_comp_list: list[tuple[Optional[str], list[CompetitorType]]] = []
    if view == "clubs":
        view_club: defaultdict[Optional[str], list[CompetitorType]] = defaultdict(list)
        for competitor in competitors:
            view_club[competitor.club_name].append(competitor)
        view_comp_list = list(view_club.items())
        view_comp_list.sort(key=lambda c: to_str(c[0]))
    elif competitors:
        view_comp_list = [("Competitors", competitors)]

    return render.competitors_table(view=view, view_comp_list=view_comp_list)


@bottle.post("/competitor/update")
def post_update() -> str:
    """Update data."""
    data = bottle.request.forms
    return update(view=data.view)


@bottle.post("/competitor/add")
def post_add() -> str | bottle.HTTPResponse:
    """Add or edit competitor."""
    data = bottle.request.forms
    try:
        if data.id == "":
            model.competitors.add_competitor(
                first_name=data.first_name,
                last_name=data.last_name,
                club_id=int(data.club_id) if data.club_id != "" else None,
                gender=data.gender,
                year=int(data.year) if data.year != "" else None,
                chip=data.chip.strip(),
            )
        else:
            model.competitors.update_competitor(
                id=int(data.id),
                first_name=data.first_name,
                last_name=data.last_name,
                club_id=int(data.club_id) if data.club_id != "" else None,
                gender=data.gender,
                year=int(data.year) if data.year != "" else None,
                chip=data.chip.strip(),
            )
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))

    return update(view=data.view)


@bottle.post("/competitor/import")
def post_import() -> str | bottle.HTTPResponse:
    """Import competitors."""
    data = bottle.request.forms
    try:
        if data.comp_import == "comp.import.1":
            with io.BytesIO() as buffer:
                bottle.request.files.browse1.save(buffer)
                competitors = iof_competitor_list.parse_competitor_list(
                    content=buffer.getvalue()
                )
            model.competitors.import_competitors(competitors=competitors)

    except Exception as e:
        return bottle.HTTPResponse(status=409, body=str(e))

    return update(view=data.view)


@bottle.post("/competitor/export")
def post_export() -> bytes | bottle.HTTPResponse:
    """Export competitors."""
    data = bottle.request.forms
    if data.comp_export == "comp.export.1":
        competitors = model.competitors.get_competitors()
        content = iof_competitor_list.create_competitor_list(competitors=competitors)

    return content


@bottle.post("/competitor/delete")
def post_delete() -> str | bottle.HTTPResponse:
    """Delete competitor."""
    data = bottle.request.forms
    try:
        model.competitors.delete_competitor(int(data.id))
        return update(view=data.view)
    except CompetitorUsedError:
        return bottle.HTTPResponse(status=409, body="Competitor used in entries")


@bottle.post("/competitor/fill_edit_form")
def post_fill_edit_form() -> str | bottle.HTTPResponse:
    """Query data to fill add or edit form."""
    data = bottle.request.forms
    if data.id == "":
        competitor = None
    else:
        competitor = model.competitors.get_competitor(int(data.id))

    clubs = model.clubs.get_clubs()
    return render.add_competitor(competitor=competitor, clubs=clubs)

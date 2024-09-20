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

from ooresults.model import model
from ooresults.plugins import iof_competitor_list
from ooresults.repo.repo import CompetitorUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


class Update:
    def POST(self):
        """Update data"""
        return render.competitors_table(model.get_competitors())


class Add:
    def POST(self):
        """Add or edit entry"""
        data = web.input()
        print(data)
        try:
            if data.id == "":
                model.add_competitor(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    club_id=int(data.club_id) if data.club_id != "" else None,
                    gender=data.gender,
                    year=int(data.year) if data.year != "" else None,
                    chip=data.chip.strip(),
                )
            else:
                model.update_competitor(
                    id=int(data.id),
                    first_name=data.first_name,
                    last_name=data.last_name,
                    club_id=int(data.club_id) if data.club_id != "" else None,
                    gender=data.gender,
                    year=int(data.year) if data.year != "" else None,
                    chip=data.chip.strip(),
                )
        except ConstraintError as e:
            raise web.conflict(str(e))
        except:
            logging.exception("Internal server error")
            raise

        return render.competitors_table(model.get_competitors())


class Import:
    def POST(self):
        """Import entries"""
        data = web.input()
        try:
            if data.comp_import == "comp.import.1":
                competitors = iof_competitor_list.parse_competitor_list(
                    content=data.browse1
                )
                model.import_competitors(competitors=competitors)

        except Exception as e:
            raise web.Conflict(str(e))

        return render.competitors_table(model.get_competitors())


class Export:
    def POST(self):
        """Export entries"""
        data = web.input()
        print("###", data)
        try:
            if data.comp_export == "comp.export.1":
                competitors = model.get_competitors()
                content = iof_competitor_list.create_competitor_list(
                    competitors=competitors
                )

        except:
            logging.exception("Internal server error")
            raise

        return content


class Delete:
    def POST(self):
        """Delete entry"""
        data = web.input()
        try:
            model.delete_competitor(int(data.id))
            return render.competitors_table(model.get_competitors())
        except CompetitorUsedError:
            raise web.conflict("Competitor used in entries")
        except:
            logging.exception("Internal server error")
            raise


class FillEditForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        if data.id == "":
            competitor = None
        else:
            competitor = model.get_competitor(int(data.id))

        clubs = model.get_clubs()
        return render.add_competitor(competitor, clubs)

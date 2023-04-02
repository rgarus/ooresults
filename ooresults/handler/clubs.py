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
from ooresults.repo.repo import ClubUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


class Update:
    def POST(self):
        """Update data"""
        return render.clubs_table(model.get_clubs())


class Add:
    def POST(self):
        """Add or edit entry"""
        data = web.input()
        print(data)
        try:
            if data.id == "":
                model.add_club(data.name)
            else:
                model.update_club(int(data.id), data.name)
        except ConstraintError as e:
            raise web.conflict(str(e))
        except:
            logging.exception("Internal server error")
            raise

        return render.clubs_table(model.get_clubs())


class Delete:
    def POST(self):
        """Delete entry"""
        data = web.input()
        print(data)
        try:
            model.delete_club(int(data.id))
            return render.clubs_table(model.get_clubs())
        except ClubUsedError:
            raise web.conflict("Club used in competitors or entries")
        except:
            logging.exception("Internal server error")
            raise


class FillEditForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        if data.id == "":
            club = Storage(
                {
                    "id": "",
                    "name": "",
                }
            )
        else:
            club = model.get_club(int(data.id))[0]

        return render.add_club(club)

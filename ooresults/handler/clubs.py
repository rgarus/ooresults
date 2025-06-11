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

import web

from ooresults import model
from ooresults.repo.repo import ClubUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.utils import render


class Update:
    def POST(self):
        """Update data"""
        return render.clubs_table(clubs=model.clubs.get_clubs())


class Add:
    def POST(self):
        """Add or edit entry"""
        data = web.input()
        print(data)
        try:
            if data.id == "":
                model.clubs.add_club(data.name)
            else:
                model.clubs.update_club(int(data.id), data.name)
        except ConstraintError as e:
            raise web.conflict(str(e))
        except KeyError:
            raise web.conflict("Club deleted")
        except:
            logging.exception("Internal server error")
            raise

        return render.clubs_table(clubs=model.clubs.get_clubs())


class Delete:
    def POST(self):
        """Delete entry"""
        data = web.input()
        print(data)
        try:
            model.clubs.delete_club(int(data.id))
            return render.clubs_table(clubs=model.clubs.get_clubs())
        except ClubUsedError:
            raise web.conflict("Club used in competitors or entries")
        except:
            logging.exception("Internal server error")
            raise


class FillEditForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        try:
            if data.id == "":
                club = None
            else:
                club = model.clubs.get_club(int(data.id))
        except KeyError:
            raise web.conflict("Club deleted")
        except:
            logging.exception("Internal server error")
            raise

        return render.add_club(club=club)

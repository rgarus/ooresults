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

import ooresults.pdf.result
import ooresults.pdf.splittimes
from ooresults import model
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import globals
from ooresults.utils import render


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1

        try:
            event, class_results = model.results.event_class_results(event_id=event_id)
            return render.results_table(event=event, class_results=class_results)
        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except:
            logging.exception("Internal server error")
            raise


class PdfResult:
    def POST(self) -> bytes:
        """Print results"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        include_dns = "res_include_dns" in data

        try:
            event, class_results = model.results.event_class_results(event_id=event_id)
            content = ooresults.pdf.result.create_pdf(
                event=event,
                results=class_results,
                include_dns=include_dns,
                landscape=len(globals.build_columns(class_results)) > 0,
            )
            return content

        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except:
            logging.exception("Internal server error")
            raise


class PdfSplittimes:
    def POST(self) -> bytes:
        """Print results"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        landscape = "res_landscape" in data

        try:
            event, class_results = model.results.event_class_results(event_id=event_id)
            content = ooresults.pdf.splittimes.create_pdf(
                event=event,
                results=class_results,
                landscape=landscape,
            )
            return content

        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except:
            logging.exception("Internal server error")
            raise

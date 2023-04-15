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
from typing import List
from typing import Dict
from typing import Tuple

import web

from ooresults.handler import model
import ooresults.pdf.result
import ooresults.pdf.splittimes
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


def build_columns(class_results: List[Tuple[Dict, Dict]]) -> set:
    columns = set()
    for class_, _ in class_results:
        if class_.params.apply_handicap_rule:
            columns.add("factor")
        if class_.params.penalty_controls is not None:
            columns.add("penalties_controls")
        if class_.params.penalty_overtime is not None:
            columns.add("penalties_overtime")
        if class_.params.otype == "score":
            columns.add("score")
    return columns


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1

        event, class_results = model.event_class_results(event_id=event_id)
        columns = build_columns(class_results)
        return render.results_table(event, class_results, columns)


class PdfResult:
    def POST(self):
        """Print results"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        include_dns = "res_include_dns" in data

        try:
            event, class_results = model.event_class_results(event_id=event_id)
            columns = build_columns(class_results)
            content = ooresults.pdf.result.create_pdf(
                event=event,
                results=class_results,
                include_dns=include_dns,
                landscape=len(columns) > 0,
            )
            return content

        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content


class PdfSplittimes:
    def POST(self):
        """Print results"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        landscape = "res_landscape" in data

        try:
            event, class_results = model.event_class_results(event_id=event_id)
            content = ooresults.pdf.splittimes.create_pdf(
                event=event,
                results=class_results,
                landscape=landscape,
            )
            return content

        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content

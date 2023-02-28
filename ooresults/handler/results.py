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
import copy
import pathlib
from typing import List
from typing import Dict
from typing import Tuple

import web

from ooresults.handler import model
from ooresults.repo.result_type import ResultStatus
import ooresults.pdf.result
import ooresults.pdf.splittimes
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


def build_results(classes: List[Dict], results: List[Dict]):
    all_results = []
    for class_ in classes:
        if class_.name == "Organizer":
            continue
        # filter results belonging to this class
        class_results = []
        for r in results:
            if r["class_"] == class_.name:
                class_results.append(r)

        if class_results != []:
            # set the time column used for sorting
            def result_equal(c1, c2) -> bool:
                if class_.params.otype == "score":
                    return (
                        c1.extensions["score"] == c2.extensions["score"]
                        and c1.time == c2.time
                    )
                else:
                    return c1.time == c2.time

            # sort the results
            if class_.params.otype == "score":
                class_results.sort(key=lambda c: c["last_name"] + "," + c["first_name"])
                class_results.sort(
                    key=lambda c: c["result"].time
                    if c["result"].time is not None
                    else 0
                )
                class_results.sort(
                    key=lambda c: c["result"].extensions["score"]
                    if c["result"].extensions.get("score", None) is not None
                    else -999999,
                    reverse=True,
                )
            else:
                class_results.sort(key=lambda c: c["last_name"] + "," + c["first_name"])
                class_results.sort(
                    key=lambda c: c["result"].time
                    if c["result"].time is not None
                    else 0
                )

            def sort_for_rank(e) -> int:
                mapping = {
                    (ResultStatus.OK, False): 0,
                    (ResultStatus.MISSING_PUNCH, False): 1,
                    (ResultStatus.OVER_TIME, False): 2,
                    (ResultStatus.DID_NOT_FINISH, False): 3,
                    (ResultStatus.DISQUALIFIED, False): 4,
                    (ResultStatus.OK, True): 5,
                    (ResultStatus.MISSING_PUNCH, True): 6,
                    (ResultStatus.OVER_TIME, True): 7,
                    (ResultStatus.DID_NOT_FINISH, True): 8,
                    (ResultStatus.DISQUALIFIED, True): 9,
                    (ResultStatus.DID_NOT_START, False): 10,
                    (ResultStatus.DID_NOT_START, True): 11,
                }
                return mapping.get((e["result"].status, e["not_competing"]), 99)

            class_results.sort(key=sort_for_rank)

            # add rank: Optional[int]
            for i, r in enumerate(class_results):
                if r["result"].status == ResultStatus.OK and not r["not_competing"]:
                    if i > 0 and result_equal(
                        class_results[i]["result"], class_results[i - 1]["result"]
                    ):
                        r["rank"] = class_results[i - 1]["rank"]
                    else:
                        r["rank"] = i + 1
                else:
                    r["rank"] = None

            # add points
            if class_.params.otype != "score":
                ref_time = class_results[0]["result"].time
                for r in class_results:
                    if r["rank"] is not None:
                        r["points"] = ref_time / r["result"].time
                    elif r["result"].status == ResultStatus.OK and r["not_competing"]:
                        r["points"] = 0
                    elif r["result"].status in (
                        ResultStatus.MISSING_PUNCH,
                        ResultStatus.DID_NOT_FINISH,
                        ResultStatus.OVER_TIME,
                        ResultStatus.DISQUALIFIED,
                    ):
                        r["points"] = 0

            all_results.append((class_, class_results))
    return all_results


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
        event = list(model.get_event(id=event_id))
        event = event[0] if event != [] else {}

        classes = list(model.get_classes(event_id=event_id))
        entry_list = list(model.get_entries(event_id=event_id))
        class_results = build_results(
            classes=classes, results=copy.deepcopy(entry_list)
        )
        columns = build_columns(class_results)
        return render.results_table(event, class_results, columns)


class PdfResult:
    def POST(self):
        """Print results"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        include_dns = "res_include_dns" in data

        try:
            event = list(model.get_event(id=event_id))
            event = event[0] if event != [] else {}
            classes = list(model.get_classes(event_id=event_id))

            entry_list = list(model.get_entries(event_id=event_id))
            class_results = build_results(classes, copy.deepcopy(entry_list))
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
            event = list(model.get_event(id=event_id))
            event = event[0] if event != [] else {}
            classes = list(model.get_classes(event_id=event_id))

            entry_list = list(model.get_entries(event_id=event_id))
            class_results = build_results(classes, copy.deepcopy(entry_list))
            content = ooresults.pdf.splittimes.create_pdf(
                event=event, results=class_results, landscape=landscape
            )
            return content

        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content

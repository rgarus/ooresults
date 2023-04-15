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


from decimal import Decimal
from typing import List
from typing import Dict
from typing import Tuple

from ooresults.repo import series_type
from ooresults.repo.result_type import ResultStatus


def build_results(
    classes: List[Dict], results: List[Dict]
) -> List[Tuple[Dict, List[Dict]]]:
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

                    if class_.params.otype != "score":
                        winner_time = class_results[0]["result"].time
                        r["time_behind"] = r["result"].time - winner_time
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


def build_total_results(
    settings: series_type.Settings, list_of_results: List, organizers: List = []
) -> List[Tuple[str, List[Dict]]]:
    q = Decimal(10) ** -settings.decimal_places

    r = {}
    for i, class_results in enumerate(list_of_results):
        for class_, results in class_results:
            if class_.name == "Organizer":
                continue
            if class_.name not in r:
                r[class_.name] = {}
            for entry in results:
                # check if competitor has points
                if entry.get("points", None) is not None:
                    if (entry["last_name"], entry["first_name"]) not in r[class_.name]:
                        r[class_.name][(entry["last_name"], entry["first_name"])] = {
                            "last_name": entry["last_name"],
                            "first_name": entry["first_name"],
                            "year": entry.get("year", None),
                            "club": entry.get("club", None),
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }

                    p = Decimal(settings.maximum_points * entry["points"]).quantize(q)
                    r[class_.name][(entry["last_name"], entry["first_name"])]["races"][
                        i
                    ] = p
            # add organizers
            if len(organizers) > i:
                for entry in organizers[i]:
                    if (entry["last_name"], entry["first_name"]) not in r[class_.name]:
                        r[class_.name][(entry["last_name"], entry["first_name"])] = {
                            "last_name": entry["last_name"],
                            "first_name": entry["first_name"],
                            "year": entry.get("year", None),
                            "club": entry.get("club", None),
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }
                    r[class_.name][(entry["last_name"], entry["first_name"])][
                        "organizer"
                    ][i] = 0

    # build sum of points
    ranked_classes = []
    for class_name, entries in r.items():
        for entry in entries.values():
            points_of_series = sorted(entry["races"].values(), reverse=True)
            # add organizer bonus
            if entry["organizer"] != {}:
                if len(points_of_series) == 0:
                    points = Decimal(0)
                elif len(points_of_series) == 1:
                    points = points_of_series[0] / 2
                else:
                    points = (points_of_series[0] + points_of_series[1]) / 2
                for i in entry["organizer"].keys():
                    entry["organizer"][i] = points.quantize(q)

            # compute sum
            points_of_series = sorted(
                list(entry["races"].values()) + list(entry["organizer"].values()),
                reverse=True,
            )
            if settings.nr_of_best_results is not None:
                points_of_series = points_of_series[0 : settings.nr_of_best_results]
            for points in points_of_series:
                entry["sum"] += points

        # build a list and rank the list
        ranked_entries = list(entries.values())
        ranked_entries.sort(key=lambda e: e["last_name"] + "," + e["first_name"])
        ranked_entries.sort(key=lambda e: e["sum"], reverse=True)

        for j, e in enumerate(ranked_entries):
            if j > 0 and ranked_entries[j]["sum"] == ranked_entries[j - 1]["sum"]:
                e["rank"] = ranked_entries[j - 1]["rank"]
            else:
                e["rank"] = j + 1
            # rank is None if sum is 0
            if e["sum"] == 0:
                e["rank"] = None

        ranked_classes.append((class_name, ranked_entries))

    return ranked_classes

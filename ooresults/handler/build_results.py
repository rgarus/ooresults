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
from typing import Optional

from ooresults.repo import series_type
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import PersonRaceResult


def build_results(
    class_infos: List[ClassInfoType],
    entries: List[EntryType],
) -> List[Tuple[ClassInfoType, List[RankedEntryType]]]:
    all_results = []
    for class_info in class_infos:
        if class_info.name == "Organizer":
            continue

        class_results: List[RankedEntryType] = []

        # filter results belonging to this class
        class_entries = [e for e in entries if e.class_name == class_info.name]
        if class_entries:
            # sort the results
            class_entries.sort(
                key=lambda e: e.last_name + "," + e.first_name,
            )
            class_entries.sort(
                key=lambda e: e.result.time if e.result.time is not None else 0,
            )
            if class_info.params.otype == "score":
                class_entries.sort(
                    key=lambda e: e.result.extensions["score"]
                    if e.result.extensions.get("score", None) is not None
                    else -999999,
                    reverse=True,
                )

            def sort_for_rank(e: EntryType) -> int:
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
                return mapping.get((e.result.status, e.not_competing), 99)

            class_entries.sort(key=sort_for_rank)

            # compute rank: Optional[int]
            for i, e in enumerate(class_entries):
                rank = None
                time_behind = None

                def result_equal(r1: PersonRaceResult, r2: PersonRaceResult) -> bool:
                    if class_info.params.otype == "score":
                        return (
                            r1.extensions["score"] == r2.extensions["score"]
                            and r1.time == r2.time
                        )
                    else:
                        return r1.time == r2.time

                winner_time = class_entries[0].result.time
                if e.result.status == ResultStatus.OK and not e.not_competing:
                    if i > 0 and result_equal(
                        class_entries[i].result, class_entries[i - 1].result
                    ):
                        rank = class_results[i - 1].rank
                    else:
                        rank = i + 1

                    if class_info.params.otype != "score":
                        time_behind = e.result.time - winner_time

                class_results.append(
                    RankedEntryType(
                        entry=e,
                        rank=rank,
                        time_behind=time_behind,
                    )
                )

        all_results.append((class_info, class_results))

    return all_results


def build_total_results(
    settings: series_type.Settings,
    list_of_results: List[List[Tuple[ClassInfoType, List[RankedEntryType]]]],
    organizers: Optional[List[List[EntryType]]] = None,
) -> List[Tuple[str, List[Dict]]]:
    if organizers is None:
        organizers = []
    q = Decimal(10) ** -settings.decimal_places

    r = {}
    for i, class_results in enumerate(list_of_results):
        for class_, ranked_entries in class_results:
            if class_.name == "Organizer":
                continue
            if class_.name not in r:
                r[class_.name] = {}

            for e in ranked_entries:
                entry = e.entry

                # compute points
                points = None
                if class_.params.otype != "score":
                    if e.rank is not None:
                        winner_time = ranked_entries[0].entry.result.time
                        points = winner_time / e.entry.result.time
                    elif entry.result.status == ResultStatus.OK and entry.not_competing:
                        points = 0
                    elif entry.result.status in (
                        ResultStatus.MISSING_PUNCH,
                        ResultStatus.DID_NOT_FINISH,
                        ResultStatus.OVER_TIME,
                        ResultStatus.DISQUALIFIED,
                    ):
                        points = 0

                # check if competitor has points
                if points is not None:
                    if (entry.last_name, entry.first_name) not in r[class_.name]:
                        r[class_.name][(entry.last_name, entry.first_name)] = {
                            "last_name": entry.last_name,
                            "first_name": entry.first_name,
                            "year": entry.year,
                            "club": entry.club_name,
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }

                    p = Decimal(settings.maximum_points * points).quantize(q)
                    r[class_.name][(entry.last_name, entry.first_name)]["races"][i] = p

            # add organizers
            if len(organizers) > i:
                for entry in organizers[i]:
                    name = (entry.last_name, entry.first_name)
                    if name not in r[class_.name]:
                        r[class_.name][name] = {
                            "last_name": entry.last_name,
                            "first_name": entry.first_name,
                            "year": entry.year,
                            "club": entry.club_name,
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }
                    r[class_.name][name]["organizer"][i] = 0

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

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
from ooresults.repo.series_type import PersonSeriesResult
from ooresults.repo.series_type import Points


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
                    (ResultStatus.FINISHED, False): 12,
                    (ResultStatus.FINISHED, True): 13,
                    (ResultStatus.ACTIVE, False): 14,
                    (ResultStatus.ACTIVE, True): 15,
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
) -> List[Tuple[str, List[PersonSeriesResult]]]:
    if organizers is None:
        organizers = []
    q = Decimal(10) ** -settings.decimal_places

    r: Dict[str, Dict[Tuple[str, str], PersonSeriesResult]] = {}
    for i, class_results in enumerate(list_of_results):
        for class_, ranked_entries in class_results:
            if class_.name == "Organizer":
                continue
            if class_.name not in r:
                r[class_.name] = {}

            # compute points
            for e in ranked_entries:
                entry = e.entry

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

                if points is not None:
                    person_name = (entry.last_name, entry.first_name)
                    if person_name not in r[class_.name]:
                        r[class_.name][person_name] = PersonSeriesResult(
                            last_name=entry.last_name,
                            first_name=entry.first_name,
                            year=entry.year,
                            club_name=entry.club_name,
                            races={},
                            total_points=Decimal(0),
                            rank=None,
                        )

                    p = Decimal(settings.maximum_points * points).quantize(q)
                    r[class_.name][person_name].races[i] = Points(points=p)

    # add organizer bonus
    for i, entries in enumerate(organizers):
        for entry in entries:
            person_name = (entry.last_name, entry.first_name)
            for class_name, person_series_results in r.items():
                if person_name in person_series_results:
                    person_series_result = person_series_results[person_name]
                    # compute organizer bonus
                    sorted_points = sorted(
                        person_series_results[person_name].races.values(),
                        key=lambda p: p.points,
                        reverse=True,
                    )
                    if len(sorted_points) == 0:
                        p = Decimal(0)
                    elif len(sorted_points) == 1:
                        p = sorted_points[0].points / 2
                    else:
                        p = (sorted_points[0].points + sorted_points[1].points) / 2

                    person_series_results[person_name].races[i] = Points(
                        points=p.quantize(q),
                        bonus=True,
                    )

    ranked_classes = []
    for class_name, person_series_results in r.items():
        # compute total points
        for person_series_result in person_series_results.values():
            sorted_points = sorted(
                person_series_result.races.values(),
                key=lambda p: p.points,
                reverse=True,
            )
            for i, points in enumerate(sorted_points):
                if (
                    settings.nr_of_best_results is None
                    or i < settings.nr_of_best_results
                ):
                    person_series_result.total_points += points.points

        # build a list and rank the list
        ranked_entries = list(person_series_results.values())
        ranked_entries.sort(key=lambda e: e.last_name + "," + e.first_name)
        ranked_entries.sort(key=lambda e: e.total_points, reverse=True)

        for j, e in enumerate(ranked_entries):
            if (
                j > 0
                and ranked_entries[j].total_points == ranked_entries[j - 1].total_points
            ):
                e.rank = ranked_entries[j - 1].rank
            else:
                e.rank = j + 1
            # rank is None if sum is 0
            if e.total_points == 0:
                e.rank = None

        ranked_classes.append((class_name, ranked_entries))

    return ranked_classes

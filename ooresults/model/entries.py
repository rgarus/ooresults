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


import copy
import datetime
import enum
import sqlite3
from typing import Optional

import tzlocal

from ooresults import model
from ooresults.model import cached_result
from ooresults.otypes import result_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.entry_type import EntryBaseDataType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.plugins import iof_result_list
from ooresults.plugins.iof_result_list import ResultListStatus
from ooresults.repo import repo
from ooresults.repo.repo import TransactionMode


def import_entries(
    event_id: int,
    entries: list[dict],
    event_key: str = None,
    clear_entries: bool = False,
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        # check if the event still exists
        event = model.db.get_event(id=event_id)
        if event_key is not None and event_key != event.key:
            raise repo.EventNotFoundError(f'Event for key "{event_key}" not found')

        # optionally, delete all entries before importing
        if clear_entries:
            model.db.delete_entries(event_id=event_id)

        competitor_ids: set[int] = set()
        list_of_entries: list[EntryBaseDataType] = []

        for c in entries:
            class_id = None
            class_ = None
            for cla in model.db.get_classes(event_id=event_id):
                if cla.name == c["class_"]:
                    class_id = cla.id
                    class_ = cla
                    break
            else:
                class_id = model.db.add_class(
                    event_id=event_id,
                    name=c["class_"],
                    short_name=None,
                    course_id=None,
                    params=ClassParams(),
                )

            club_id = None
            if c["club"]:
                for clb in model.db.get_clubs():
                    if clb.name == c["club"]:
                        club_id = clb.id
                        break
                else:
                    club_id = model.db.add_club(c["club"])

            gender = c["gender"] if "gender" in c else ""
            year = c["year"] if "year" in c else None
            competitor = model.db.get_competitor_by_name(
                first_name=c["first_name"],
                last_name=c["last_name"],
            )
            if competitor:
                competitor_id = competitor.id
                # update gender and year in competitor
                gender = gender if gender != "" else competitor.gender
                year = year if year is not None else competitor.year
                if gender != competitor.gender or year != competitor.year:
                    model.db.update_competitor(
                        id=competitor.id,
                        first_name=competitor.first_name,
                        last_name=competitor.last_name,
                        club_id=competitor.club_id,
                        gender=gender,
                        year=year,
                        chip=competitor.chip,
                    )
            else:
                competitor_id = model.db.add_competitor(
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                    club_id=club_id,
                    gender=gender,
                    year=year,
                    chip=c["chip"] if "chip" in c else "",
                )

            # update result
            if c["result"].has_punches():
                try:
                    course_id = class_["course_id"]
                    class_params = class_["params"]
                    controls = model.db.get_course(id=course_id).controls
                except Exception:
                    class_params = ClassParams()
                    controls = []
                c["result"].compute_result(
                    controls=controls,
                    class_params=class_params,
                    start_time=c["result"].start_time,
                    year=year,
                    gender=gender if gender != "" else None,
                )

            entries_by_name = model.db.get_entries_by_name(
                event_id=event_id,
                first_name=c["first_name"],
                last_name=c["last_name"],
            )

            if entries_by_name:
                # Check that each competitor has only one entry
                # Otherwise, an entry might be incorrectly assigned to an existing entry
                if len(entries_by_name) >= 2 or competitor_id in competitor_ids:
                    raise repo.ConstraintError("Ambiguous update")

                not_competing = entries_by_name[0].not_competing
                if "not_competing" in c:
                    not_competing = c["not_competing"]
                chip = entries_by_name[0].chip
                if "chip" in c:
                    chip = c["chip"]
                fields = entries_by_name[0].fields
                if "fields" in c:
                    fields = copy.deepcopy(c["fields"])
                result = entries_by_name[0].result
                if "result" in c:
                    result = copy.deepcopy(c["result"])
                start = entries_by_name[0].start
                if "start" in c:
                    start = copy.deepcopy(c["start"])

                competitor_ids.add(competitor_id)
                model.db.update_entry(
                    id=entries_by_name[0].id,
                    class_id=class_id,
                    club_id=club_id,
                    not_competing=not_competing,
                    chip=chip,
                    fields=fields,
                    result=result,
                    start=start,
                )

            else:
                entry_data = EntryBaseDataType(
                    event_id=event_id,
                    competitor_id=competitor_id,
                    class_id=class_id,
                    club_id=club_id,
                )
                if "result" in c:
                    entry_data.result = copy.deepcopy(c["result"])
                if "start" in c:
                    entry_data.start = copy.deepcopy(c["start"])
                if "chip" in c:
                    entry_data.chip = c["chip"]
                if "fields" in c:
                    entry_data.fields = copy.deepcopy(c["fields"])
                if "not_competing" in c:
                    entry_data.not_competing = c["not_competing"]

                list_of_entries.append(entry_data)

        if list_of_entries:
            model.db.add_many_entries(list_of_entries=list_of_entries)

    cached_result.clear_cache(event_id=event_id)


def import_iof_result_list(event_key: str, content: bytes) -> None:
    #
    # 1. Find event corresponding to event_key
    # 2. Decode IOF xml data
    # 3. Import entries
    #
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in model.db.get_events():
            if event_key != "" and e.key == event_key:
                event_id = e.id
                break
        else:
            raise repo.EventNotFoundError(f'Event for key "{event_key}" not found')

    _, entries, status = iof_result_list.parse_result_list(content)
    import_entries(
        event_id=event_id,
        entries=entries,
        event_key=event_key,
        clear_entries=status != ResultListStatus.DELTA,
    )
    cached_result.clear_cache(event_id=event_id)


def get_entries(event_id: int) -> list[EntryType]:
    with model.db.transaction():
        return model.db.get_entries(event_id=event_id)


def get_entry(id: int) -> EntryType:
    with model.db.transaction():
        return model.db.get_entry(id=id)


def add_or_update_entry(
    id: Optional[int],
    event_id: int,
    competitor_id: Optional[int],
    first_name: str,
    last_name: str,
    gender: str,
    year: Optional[int],
    class_id: int,
    club_id: Optional[int],
    not_competing: bool,
    chip: str,
    fields: dict[int, str],
    status: ResultStatus,
    start_time: Optional[datetime.datetime],
    result_id: Optional[int],
) -> tuple[int, bool]:
    """Add a new entry to an event or update an existing entry of an event."""
    #
    # result_id == -1: remove result from entry (store as pseudy result)
    #

    nc_changed = False
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        try:
            if id is None:
                if competitor_id is None:
                    com = model.db.get_competitor_by_name(
                        first_name=first_name,
                        last_name=last_name,
                    )
                    if com:
                        competitor_id = com.id
                        if gender == "":
                            gender = com.gender
                        if year is None:
                            year = com.year
                        if chip == "":
                            chip = com.chip
                        if club_id is None:
                            club_id = com.club_id
                    else:
                        competitor_id = model.db.add_competitor(
                            first_name=first_name,
                            last_name=last_name,
                            club_id=club_id,
                            gender=gender,
                            year=year,
                            chip=chip,
                        )

                competitor = model.db.get_competitor(id=competitor_id)
                if competitor.club_id is None:
                    competitor.club_id = club_id
                if competitor.chip == "":
                    competitor.chip = chip
                model.db.update_competitor(
                    id=competitor.id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    year=year,
                    club_id=competitor.club_id,
                    chip=competitor.chip,
                )

                entry_ids = model.db.get_entry_ids_by_competitor(
                    event_id=event_id,
                    competitor_id=competitor_id,
                )
                nc_changed = entry_ids != [] and not not_competing
                id = model.db.add_entry(
                    event_id=event_id,
                    competitor_id=competitor_id,
                    class_id=class_id,
                    club_id=club_id,
                    not_competing=not_competing or entry_ids != [],
                    chip=chip,
                    fields=fields,
                    result=PersonRaceResult(status=status),
                    start=PersonRaceStart(start_time=start_time),
                )
                result = PersonRaceResult()
            else:
                entry = model.db.get_entry(id=id)
                result = entry.result
                if result_id is not None:
                    # store result as new entry
                    r = copy.deepcopy(result)
                    r.reset()
                    if r.has_punches():
                        r.compute_result(controls=[], class_params=ClassParams())
                        model.db.add_entry_result(
                            event_id=entry.event_id,
                            chip=entry.chip,
                            result=r,
                            start=PersonRaceStart(),
                        )

                competitor = model.db.get_competitor(id=entry.competitor_id)
                model.db.update_competitor(
                    id=competitor.id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    year=year,
                    club_id=competitor.club_id,
                    chip=competitor.chip,
                )

                r = copy.deepcopy(entry.result)
                r.status = status
                s = copy.deepcopy(entry.start)
                s.start_time = start_time

                model.db.update_entry(
                    id=id,
                    class_id=class_id,
                    club_id=club_id,
                    not_competing=not_competing,
                    chip=chip,
                    fields=fields,
                    result=r,
                    start=s,
                )

            old_status = result.status

            # update result if result_id is defined
            if result_id == -1:
                # result will be removed
                result = PersonRaceResult()
            elif result_id is not None:
                # result will be replaced
                try:
                    result_entry = model.db.get_entry(id=result_id)
                    model.db.delete_entry(id=result_id)

                    chip = result_entry.chip
                    result = result_entry.result
                except KeyError:
                    raise repo.ConstraintError("Result deleted")

            # update result status
            if (
                result_id != -1
                or status != old_status
                or status == ResultStatus.DISQUALIFIED
            ):
                result.status = status

            # compute new result
            try:
                class_ = model.db.get_class(id=class_id)
                course_id = class_.course_id
                class_params = class_.params
                controls = model.db.get_course(id=course_id).controls
            except KeyError:
                class_params = ClassParams()
                controls = []

            result.compute_result(
                controls=controls,
                class_params=class_params,
                start_time=start_time,
                year=year,
                gender=gender if gender != "" else None,
            )
            model.db.update_entry_result(
                id=id,
                chip=chip,
                result=result,
                start=PersonRaceStart(start_time=start_time),
            )

        except (sqlite3.IntegrityError, repo.ConstraintError, KeyError):
            # check if the event still exists
            model.db.get_event(id=event_id)

            # check if the entry still exists
            if id is not None:
                try:
                    model.db.get_entry(id=id)
                except KeyError:
                    raise repo.ConstraintError("Entry deleted")

            # check if the competitor still exists
            if competitor_id is not None:
                try:
                    model.db.get_competitor(id=competitor_id)
                except KeyError:
                    raise repo.ConstraintError("Competitor deleted")

            # check if the class still exists
            try:
                model.db.get_class(id=class_id)
            except KeyError:
                raise repo.ConstraintError("Class deleted")

            # check if the club still exists
            if club_id is not None:
                try:
                    model.db.get_club(id=club_id)
                except KeyError:
                    raise repo.ConstraintError("Club deleted")

            raise

    cached_result.clear_cache(event_id=event_id, entry_id=id)
    return id, nc_changed


@enum.unique
class EditEntryResultCommand(enum.Enum):
    EDIT = enum.auto()
    DELETE = enum.auto()
    ADD_BEFORE = enum.auto()


def edit_entry_result(
    entry_id: int,
    event_id: int,
    command: str,
    control: str,
    selected_row: int | str,
    punch_time: Optional[datetime.time],
) -> EntryType:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        event = model.db.get_event(id=event_id)
        entry = model.db.get_entry(id=entry_id)
        result = entry.result
        split_times = result.split_times

        if selected_row == "START":
            # update changed start time
            if punch_time is None:
                result.punched_start_time = None
            elif (
                result.punched_start_time is None
                or result.punched_start_time.time() != punch_time
            ):
                result.punched_start_time = datetime.datetime.combine(
                    date=event.date,
                    time=punch_time,
                    tzinfo=tzlocal.get_localzone(),
                )
        elif selected_row == "FINISH":
            # update changed finish time
            if punch_time is None:
                result.punched_finish_time = None
            elif (
                result.punched_finish_time is None
                or result.punched_finish_time.time() != punch_time
            ):
                result.punched_finish_time = datetime.datetime.combine(
                    date=event.date,
                    time=punch_time,
                    tzinfo=tzlocal.get_localzone(),
                )
        else:
            if command == "entr_ep_del":
                if split_times[selected_row].si_punch_time is None:
                    # delete the row (punch not contained at SI card)
                    split_times.pop(selected_row)
                else:
                    # delete the used punch time
                    split_times[selected_row].punch_time = None
            else:
                if punch_time is None:
                    used_t = result_type.SplitTime.NO_TIME
                else:
                    used_t = datetime.datetime.combine(
                        date=event.date,
                        time=punch_time,
                        tzinfo=tzlocal.get_localzone(),
                    )

                if command == "entr_ep_edit":
                    split_times[selected_row].punch_time = used_t
                else:
                    split_times.insert(
                        selected_row,
                        SplitTime(control_code=control, punch_time=used_t),
                    )

        # compute new result
        try:
            class_ = model.db.get_class(id=entry.class_id)
            course_id = class_.course_id
            class_params = class_.params
            controls = model.db.get_course(id=course_id).controls
        except KeyError:
            class_params = ClassParams()
            controls = []

        result.compute_result(
            controls=controls,
            class_params=class_params,
            start_time=entry.start.start_time,
            year=int(entry.year) if entry.year is not None else None,
            gender=entry.gender,
        )

        # store result
        model.db.update_entry_result(
            id=entry.id,
            chip=entry.chip,
            result=result,
            start=entry.start,
        )

    cached_result.clear_cache(event_id=event_id, entry_id=entry_id)
    return entry


def delete_entries(event_id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_entries(event_id=event_id)

    cached_result.clear_cache(event_id=event_id)


def delete_entry(id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_entry(id=id)
    cached_result.clear_cache()

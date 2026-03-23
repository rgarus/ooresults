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
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo import repo
from ooresults.repo.repo import TransactionMode


def import_entries(event_id: int, entries: list[dict]) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.import_entries(event_id=event_id, entries=entries)

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

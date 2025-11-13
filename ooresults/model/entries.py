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
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import tzlocal

from ooresults import model
from ooresults.model import cached_result
from ooresults.otypes import result_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.repo.repo import TransactionMode


def import_entries(event_id: int, entries: List[Dict]) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.import_entries(event_id=event_id, entries=entries)

    cached_result.clear_cache(event_id=event_id)


def get_entries(event_id: int) -> List[EntryType]:
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
    fields: Dict[int, str],
    status: ResultStatus,
    start_time: Optional[datetime.datetime],
    result_id: Optional[int],
) -> int:
    #
    # result_id == -1: remove result from entry (store as pseudy result)
    #

    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        if id is None:
            id = model.db.add_entry(
                event_id=event_id,
                competitor_id=competitor_id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                year=year,
                class_id=class_id,
                club_id=club_id,
                not_competing=not_competing,
                chip=chip,
                fields=fields,
                status=status,
                start_time=start_time,
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
                        start_time=None,
                    )

            model.db.update_entry(
                id=id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                year=year,
                class_id=class_id,
                club_id=club_id,
                not_competing=not_competing,
                chip=chip,
                fields=fields,
                status=status,
                start_time=start_time,
            )

        old_status = result.status

        # update entry result
        if result_id == -1:
            # result will be removed
            result = PersonRaceResult()
        elif result_id is not None:
            # result will be replaced
            e = model.db.get_entry(id=result_id)
            chip = e.chip
            result = e.result
            model.db.delete_entry(id=result_id)

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
            start_time=start_time,
        )

    cached_result.clear_cache(event_id=event_id, entry_id=id)
    return id


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
    selected_row: Union[int, str],
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
            start_time=entry.start.start_time,
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

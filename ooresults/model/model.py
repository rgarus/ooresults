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


import asyncio
import copy
import datetime
import enum
import json
import pathlib
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import iso8601
import jsonschema
import tzlocal

from ooresults.model import build_results
from ooresults.model.build_results import PersonSeriesResult
from ooresults.plugins import iof_result_list
from ooresults.plugins.iof_result_list import ResultListStatus
from ooresults.repo import result_type
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.class_type import ClassType
from ooresults.repo.club_type import ClubType
from ooresults.repo.competitor_type import CompetitorType
from ooresults.repo.course_type import CourseType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import TransactionMode
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SpStatus
from ooresults.repo.result_type import SplitTime
from ooresults.repo.series_type import Settings
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.websocket_server.websocket_server import WebSocketServer


websocket_server: Optional[WebSocketServer] = None
db: Optional[SqliteRepo] = None


data_path = (
    pathlib.Path(__file__).resolve().parent.parent / "schema" / "cardreader_log.json"
)
with open(data_path, "r") as f:
    schema_cardreader_log = json.loads(f.read())


def get_classes(event_id: int) -> List[ClassInfoType]:
    with db.transaction():
        return db.get_classes(event_id=event_id)


def get_class(id: int) -> ClassType:
    with db.transaction():
        return db.get_class(id=id)


def import_classes(event_id: int, classes: List[Dict]) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_classes = db.get_classes(event_id=event_id)
        for c in classes:
            for cl in existing_classes:
                if cl.name == c["name"]:
                    db.update_class(
                        id=cl.id,
                        name=cl.name,
                        short_name=c["short_name"]
                        if c.get("short_name", None) is not None
                        else cl.short_name,
                        course_id=cl.course_id,
                        params=cl.params,
                    )
                    break
            else:
                id = db.add_class(
                    event_id=event_id,
                    name=c["name"],
                    short_name=c.get("short_name", None),
                    course_id=None,
                    params=ClassParams(),
                )


def add_class(
    event_id: int,
    name: str,
    short_name: Optional[str],
    course_id: Optional[int],
    params: ClassParams,
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_class(
            event_id=event_id,
            name=name,
            short_name=short_name,
            course_id=course_id,
            params=params,
        )


def update_class(
    id: int,
    event_id: int,
    name: str,
    short_name: Optional[str],
    course_id: Optional[int],
    params: ClassParams,
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        # update class data
        try:
            db.update_class(
                id=id,
                name=name,
                short_name=short_name,
                course_id=course_id,
                params=params,
            )
        except KeyError:
            # distinguish between 'Event deleted' or 'Class deleted'
            db.get_event(id=event_id)
            raise

        # update results of the competitors belonging to the modified class
        try:
            class_params = params
            controls = db.get_course(id=course_id).controls
        except:
            class_params = ClassParams()
            controls = []

        entries = db.get_entries(event_id=event_id)
        for entry in entries:
            if entry.class_id == id:
                entry.result.compute_result(
                    controls=controls,
                    class_params=class_params,
                    start_time=entry.start.start_time,
                    year=entry.year,
                    gender=entry.gender if entry.gender != "" else None,
                )
                db.update_entry_result(
                    id=entry.id,
                    chip=entry.chip,
                    result=entry.result,
                    start_time=entry.start.start_time,
                )


def delete_classes(event_id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_classes(event_id=event_id)


def delete_class(id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_class(id=id)


def get_courses(event_id: int) -> List[CourseType]:
    with db.transaction():
        return db.get_courses(event_id=event_id)


def get_course(id: int) -> CourseType:
    with db.transaction():
        return db.get_course(id=id)


def import_courses(
    event_id: int, courses: List[Dict], class_course: List[Dict]
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_courses = db.get_courses(event_id=event_id)
        for c in courses:
            for co in existing_courses:
                if co.name == c["name"]:
                    db.update_course(
                        id=co.id,
                        name=co.name,
                        length=c.get("length", None),
                        climb=c.get("climb", None),
                        controls=c["controls"],
                    )
                    break
            else:
                id = db.add_course(
                    event_id=event_id,
                    name=c["name"],
                    length=c.get("length", None),
                    climb=c.get("climb", None),
                    controls=c["controls"],
                )
        existing_classes = db.get_classes(event_id=event_id)
        existing_courses = db.get_courses(event_id=event_id)
        for i in class_course:
            for co in existing_courses:
                if co.name == i.get("course_name", None):
                    for cl in existing_classes:
                        if cl.name == i["class_name"]:
                            db.update_class(
                                id=cl.id,
                                name=cl.name,
                                short_name=cl.short_name,
                                course_id=co.id,
                                params=cl.params,
                            )
                            break
                    else:
                        id = db.add_class(
                            event_id=event_id,
                            name=i["class_name"],
                            short_name=None,
                            course_id=co.id,
                            params=ClassParams(),
                        )
                    break
            else:
                if i["course_name"] is None:
                    for cl in existing_classes:
                        if cl.name == i["class_name"]:
                            db.update_class(
                                id=cl.id,
                                name=cl.name,
                                short_name=cl.short_name,
                                course_id=None,
                                params=cl.params,
                            )
                            break
                    else:
                        id = db.add_class(
                            event_id=event_id,
                            name=i["class_name"],
                            short_name=None,
                            course_id=None,
                            params=ClassParams(),
                        )


def add_course(
    event_id: int,
    name: str,
    length: Optional[float],
    climb: Optional[float],
    controls: List[str],
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_course(
            event_id=event_id,
            name=name,
            length=length,
            climb=climb,
            controls=controls,
        )


def update_course(
    id: int,
    event_id: int,
    name: str,
    length: Optional[float],
    climb: Optional[float],
    controls: List[str],
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        # update course data
        try:
            db.update_course(
                id=id,
                name=name,
                length=length,
                climb=climb,
                controls=controls,
            )
        except KeyError:
            # distinguish between 'Event deleted' or 'Course deleted'
            db.get_event(id=event_id)
            raise

        # update results of the competitors belonging to a class using the modified course
        classes = db.get_classes(event_id=event_id)
        classes = [c for c in classes if c.course_id == id]

        entries = db.get_entries(event_id=event_id)
        for entry in entries:
            for class_ in classes:
                if entry.class_id == class_.id:
                    entry.result.compute_result(
                        controls=controls,
                        class_params=class_.params,
                        start_time=entry.start.start_time,
                        year=entry.year,
                        gender=entry.gender if entry.gender != "" else None,
                    )
                    db.update_entry_result(
                        id=entry.id,
                        chip=entry.chip,
                        result=entry.result,
                        start_time=entry.start.start_time,
                    )
                    break


def delete_courses(event_id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_courses(event_id=event_id)


def delete_course(id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_course(id=id)


def get_clubs() -> List[ClubType]:
    with db.transaction():
        return db.get_clubs()


def get_club(id: int) -> ClubType:
    with db.transaction():
        return db.get_club(id=id)


def add_club(name) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_club(name=name)


def update_club(id, name) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_club(id=id, name=name)


def delete_club(id) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_club(id=id)


def get_competitors() -> List[CompetitorType]:
    with db.transaction():
        return db.get_competitors()


def get_competitor(id: int) -> CompetitorType:
    with db.transaction():
        return db.get_competitor(id=id)


def add_competitor(first_name, last_name, club_id, gender, year, chip):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_competitor(
            first_name=first_name,
            last_name=last_name,
            club_id=club_id,
            gender=gender,
            year=year,
            chip=chip,
        )


def update_competitor(id, first_name, last_name, club_id, gender, year, chip):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_competitor(
            id=id,
            first_name=first_name,
            last_name=last_name,
            club_id=club_id,
            gender=gender,
            year=year,
            chip=chip,
        )


def delete_competitor(id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_competitor(id=id)


def import_competitors(competitors) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.import_competitors(competitors)


def import_entries(event_id: int, entries: List[Dict]) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.import_entries(event_id=event_id, entries=entries)


def get_entries(event_id: int) -> List[EntryType]:
    with db.transaction():
        return db.get_entries(event_id=event_id)


def get_entry(id: int) -> EntryType:
    with db.transaction():
        return db.get_entry(id=id)


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

    with db.transaction(mode=TransactionMode.IMMEDIATE):
        if id is None:
            id = db.add_entry(
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
            entry = db.get_entry(id=id)
            result = entry.result
            if result_id is not None:
                # store result as new entry
                r = copy.deepcopy(result)
                r.reset()
                if r.has_punches():
                    r.compute_result(controls=[], class_params=ClassParams())
                    db.add_entry_result(
                        event_id=entry.event_id,
                        chip=entry.chip,
                        result=r,
                        start_time=None,
                    )

            db.update_entry(
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
            e = db.get_entry(id=result_id)
            chip = e.chip
            result = e.result
            db.delete_entry(id=result_id)

        # update result status
        if (
            result_id != -1
            or status != old_status
            or status == ResultStatus.DISQUALIFIED
        ):
            result.status = status

        # compute new result
        try:
            class_ = db.get_class(id=class_id)
            course_id = class_.course_id
            class_params = class_.params
            controls = db.get_course(id=course_id).controls
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
        db.update_entry_result(
            id=id,
            chip=chip,
            result=result,
            start_time=start_time,
        )
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
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        event = db.get_event(id=event_id)
        entry = db.get_entry(id=entry_id)
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
            class_ = db.get_class(id=entry.class_id)
            course_id = class_.course_id
            class_params = class_.params
            controls = db.get_course(id=course_id).controls
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
        db.update_entry_result(
            id=entry.id,
            chip=entry.chip,
            result=result,
            start_time=entry.start.start_time,
        )
        return entry


def delete_entries(event_id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entries(event_id=event_id)


def delete_entry(id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entry(id=id)


def get_events() -> List[EventType]:
    with db.transaction():
        return db.get_events()


def get_event(id: int) -> EventType:
    with db.transaction():
        return db.get_event(id=id)


def add_event(
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: List[str],
    streaming_address: Optional[str] = None,
    streaming_key: Optional[str] = None,
    streaming_enabled: Optional[bool] = None,
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        id = db.add_event(
            name=name,
            date=date,
            key=key,
            publish=publish,
            series=series,
            fields=fields,
            streaming_address=streaming_address,
            streaming_key=streaming_key,
            streaming_enabled=streaming_enabled,
        )
    future = asyncio.run_coroutine_threadsafe(
        coro=websocket_server.update_event(
            event=EventType(
                id=id,
                name=name,
                date=date,
                key=key,
                publish=publish,
                series=series,
                fields=fields,
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )
        ),
        loop=websocket_server.loop,
    )
    future.result()


def update_event(
    id: int,
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: List[str],
    streaming_address: Optional[str] = None,
    streaming_key: Optional[str] = None,
    streaming_enabled: Optional[bool] = None,
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_event(
            id=id,
            name=name,
            date=date,
            key=key,
            publish=publish,
            series=series,
            fields=fields,
            streaming_address=streaming_address,
            streaming_key=streaming_key,
            streaming_enabled=streaming_enabled,
        )

    future = asyncio.run_coroutine_threadsafe(
        coro=websocket_server.update_event(
            event=EventType(
                id=id,
                name=name,
                date=date,
                key=key,
                publish=publish,
                series=series,
                fields=fields,
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )
        ),
        loop=websocket_server.loop,
    )
    future.result()


def delete_event(id: int) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entries(event_id=id)
        db.delete_classes(event_id=id)
        db.delete_courses(event_id=id)
        db.delete_event(id)


def parse_cardreader_log(item: Dict) -> result_type.CardReaderMessage:
    jsonschema.validate(item, schema_cardreader_log)
    d = result_type.CardReaderMessage(
        entry_type=item["entryType"],
        entry_time=iso8601.parse_date(item["entryTime"]),
        control_card=item.get("controlCard", None),
        result=None,
    )

    if d.entry_type == "cardRead":
        result = result_type.PersonRaceResult(status=ResultStatus.FINISHED)
        if item.get("clearTime", None) is not None:
            result.punched_clear_time = iso8601.parse_date(item["clearTime"])
        if item.get("checkTime", None) is not None:
            result.punched_check_time = iso8601.parse_date(item["checkTime"])
        if item.get("startTime", None) is not None:
            result.punched_start_time = iso8601.parse_date(item["startTime"])
            result.si_punched_start_time = result.punched_start_time
        if item.get("finishTime", None) is not None:
            result.punched_finish_time = iso8601.parse_date(item["finishTime"])
            result.si_punched_finish_time = result.punched_finish_time
        result.start_time = result.punched_start_time
        result.finish_time = result.punched_finish_time
        for p in item["punches"]:
            result.split_times.append(
                result_type.SplitTime(
                    control_code=p["controlCode"],
                    punch_time=iso8601.parse_date(p["punchTime"]),
                    si_punch_time=iso8601.parse_date(p["punchTime"]),
                    status=SpStatus.ADDITIONAL,
                )
            )
        d.result = result

    return d


def store_cardreader_result(
    event_key: str, item: result_type.CardReaderMessage
) -> Tuple[str, EventType, Dict]:
    def missing_controls(result: result_type.PersonRaceResult) -> List[str]:
        if result.finish_time is None:
            return ["FINISH"]
        if result.start_time is None:
            return ["START"]
        controls = []
        for sp in result.split_times:
            if sp.status == SpStatus.MISSING:
                controls.append(sp.control_code)
        return controls

    with db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in db.get_events():
            if event_key != "" and e.key == event_key:
                event = e
                break
        else:
            raise EventNotFoundError(f'Event for key "{event_key}" not found')

        if item.entry_type == "cardRead":
            result = item.result

            entries = db.get_entries(event_id=event.id)
            entries_control_card = [e for e in entries if e.chip == item.control_card]
            assigned_entries = [
                e for e in entries_control_card if e.class_name is not None
            ]
            unassigned_entries = [
                e for e in entries_control_card if e.class_name is None
            ]

            for entry in assigned_entries:
                r = entry.result
                if r is not None and r.same_si_punches(other=result):
                    # result exists and is assigned to a competitor => nothing to do
                    res = {
                        "entryTime": item.entry_time,
                        "eventId": event.id,
                        "controlCard": entry.chip,
                        "firstName": entry.first_name,
                        "lastName": entry.last_name,
                        "club": entry.club_name,
                        "class": entry.class_name,
                        "status": r.status,
                        "time": r.extensions.get("running_time", r.time),
                        "error": None,
                        "missingControls": missing_controls(result=r),
                    }
                    break
            else:
                # check if result is already read out
                unassigned_entry = None
                for entry in unassigned_entries:
                    if entry.result.same_si_punches(other=result):
                        unassigned_entry = entry
                        break

                # result can be assigned to an entry if
                #   (1) there is exactly one entry without result
                #   (2) there is no unassigned entry or one unassigned entry with same result
                if (
                    len(assigned_entries) == 1
                    and not assigned_entries[0].result.has_punches()
                    and (
                        len(unassigned_entries) == 0
                        or len(unassigned_entries) == 1
                        and unassigned_entries[0].result.same_si_punches(other=result)
                    )
                ):
                    entry = assigned_entries[0]
                    try:
                        class_ = db.get_class(id=entry.class_id)
                        course_id = class_.course_id
                        class_params = class_.params
                        controls = db.get_course(id=course_id).controls
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
                    db.update_entry_result(
                        id=entry.id,
                        chip=entry.chip,
                        result=result,
                        start_time=entry.start.start_time,
                    )
                    res = {
                        "entryTime": item.entry_time,
                        "eventId": event.id,
                        "controlCard": entry.chip,
                        "firstName": entry.first_name,
                        "lastName": entry.last_name,
                        "club": entry.club_name,
                        "class": entry.class_name,
                        "status": result.status,
                        "time": result.extensions.get("running_time", result.time),
                        "error": None,
                        "missingControls": missing_controls(result=result),
                    }

                    # if there is an unassigned entry with the same result, delete it
                    if unassigned_entries == [unassigned_entry]:
                        db.delete_entry(id=unassigned_entry.id)

                else:
                    # create a new unassigned entry
                    result.compute_result(controls=[], class_params=ClassParams())
                    if unassigned_entry is None:
                        db.add_entry_result(
                            event_id=event.id,
                            chip=item.control_card,
                            result=result,
                            start_time=None,
                        )
                    res = {
                        "entryTime": item.entry_time,
                        "eventId": event.id,
                        "controlCard": item.control_card,
                        "firstName": None,
                        "lastName": None,
                        "club": None,
                        "class": None,
                        "status": result.status,
                        "time": None,
                    }
                    if len(assigned_entries) == 0:
                        res["error"] = "Control card unknown"
                    elif len(assigned_entries) >= 2:
                        res["error"] = "There are several entries for this card"
                    else:
                        res["error"] = "There are other results for this card"

        elif item.entry_type == "cardInserted":
            res = {"eventId": event.id, "controlCard": item.control_card}
        else:
            res = {"eventId": event.id}

    return item.entry_type, event, res


def get_series_settings() -> Settings:
    with db.transaction():
        return db.get_series_settings()


def update_series_settings(settings: Settings) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_series_settings(settings=settings)


def event_class_results(
    event_id: int,
) -> Tuple[EventType, List[Tuple[ClassInfoType, List[RankedEntryType]]]]:
    with db.transaction():
        event = db.get_event(id=event_id)
        classes = db.get_classes(event_id=event_id)
        entries = db.get_entries(event_id=event_id)

    class_results = build_results.build_results(
        class_infos=classes,
        entries=copy.deepcopy(entries),
    )
    return event, class_results


def results_for_splitsbrowser(
    event_id: int,
) -> Tuple[EventType, List[Tuple[ClassInfoType, List[RankedEntryType]]]]:
    with db.transaction():
        event = db.get_event(id=event_id)
        classes = db.get_classes(event_id=event_id)
        entries = copy.deepcopy(db.get_entries(event_id=event_id))

    # filter entries - use only finished entries
    entries = [
        e
        for e in entries
        if e.result.status
        not in (
            ResultStatus.INACTIVE,
            ResultStatus.ACTIVE,
            ResultStatus.DID_NOT_START,
        )
    ]

    # compute result time without handicap factor, penalties or credits
    for e in entries:
        if e.result.start_time is not None and e.result.finish_time is not None:
            e.result.time = int(
                (e.result.finish_time - e.result.start_time).total_seconds()
            )

    class_results = build_results.build_results(
        class_infos=classes,
        entries=entries,
    )
    return event, class_results


def create_event_list(events: List[EventType]) -> List[EventType]:
    # filter list
    e_list = [e for e in events if e.series is not None]
    # sort list
    e_list.sort(key=lambda e: e.series)
    e_list.sort(key=lambda e: e.date)
    return e_list


def build_series_result() -> (
    Tuple[Settings, List[EventType], List[Tuple[str, List[PersonSeriesResult]]]]
):
    with db.transaction():
        settings = db.get_series_settings()
        # build event list
        events = db.get_events()
        events = create_event_list(events=events)

        list_of_results = []
        organizers = []
        for i, event in enumerate(events):
            classes = db.get_classes(event_id=event.id)
            entries = db.get_entries(event_id=event.id)
            class_results = build_results.build_results(
                class_infos=classes,
                entries=copy.deepcopy(entries),
            )
            list_of_results.append(class_results)
            organizers.append([e for e in entries if e.class_name == "Organizer"])

    ranked_classes = build_results.build_total_results(
        settings=settings,
        list_of_results=list_of_results,
        organizers=organizers,
    )
    return (
        settings,
        events,
        ranked_classes,
    )


def import_iof_result_list(event_key: str, content: bytes) -> None:
    #
    # 1. Find event corresponding to event_key
    # 2. Decode IOF xml data
    # 3. Delete all entries of the event
    # 4. Delete all classes of the event
    # 5. Import entries
    #
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in db.get_events():
            if event_key != "" and e.key == event_key:
                event = e
                break
        else:
            raise EventNotFoundError(f'Event for key "{event_key}" not found')

        _, entries, status = iof_result_list.parse_result_list(content)
        if status != ResultListStatus.DELTA:
            db.delete_entries(event_id=event.id)
            db.delete_classes(event_id=event.id)
        db.import_entries(event_id=event.id, entries=entries)

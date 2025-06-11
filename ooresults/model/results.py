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
import json
import pathlib
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import iso8601
import jsonschema

from ooresults import model
from ooresults.handler import cached_result
from ooresults.model import build_results
from ooresults.model.build_results import PersonSeriesResult
from ooresults.otypes import result_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SpStatus
from ooresults.otypes.series_type import Settings
from ooresults.plugins import iof_result_list
from ooresults.plugins.iof_result_list import ResultListStatus
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import TransactionMode
from ooresults.websocket_server.websocket_server import WebSocketServer


websocket_server: Optional[WebSocketServer] = None


data_path = (
    pathlib.Path(__file__).resolve().parent.parent / "schema" / "cardreader_log.json"
)
with open(data_path, "r") as f:
    schema_cardreader_log = json.loads(f.read())


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

    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in model.db.get_events():
            if event_key != "" and e.key == event_key:
                event = e
                break
        else:
            raise EventNotFoundError(f'Event for key "{event_key}" not found')

        if item.entry_type == "cardRead":
            result = item.result

            entries = model.db.get_entries(event_id=event.id)
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
                    model.db.update_entry_result(
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
                    cached_result.clear_cache(event_id=event.id, entry_id=entry.id)

                    # if there is an unassigned entry with the same result, delete it
                    if unassigned_entries == [unassigned_entry]:
                        model.db.delete_entry(id=unassigned_entry.id)

                else:
                    # create a new unassigned entry
                    result.compute_result(controls=[], class_params=ClassParams())
                    if unassigned_entry is None:
                        model.db.add_entry_result(
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
    with model.db.transaction():
        return model.db.get_series_settings()


def update_series_settings(settings: Settings) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.update_series_settings(settings=settings)


def event_class_results(
    event_id: int,
) -> Tuple[EventType, List[Tuple[ClassInfoType, List[RankedEntryType]]]]:
    with model.db.transaction():
        event = model.db.get_event(id=event_id)
        classes = model.db.get_classes(event_id=event_id)
        entries = model.db.get_entries(event_id=event_id)

    class_results = build_results.build_results(
        class_infos=classes,
        entries=copy.deepcopy(entries),
    )
    return event, class_results


def results_for_splitsbrowser(
    event_id: int,
) -> Tuple[EventType, List[Tuple[ClassInfoType, List[RankedEntryType]]]]:
    with model.db.transaction():
        event = model.db.get_event(id=event_id)
        classes = model.db.get_classes(event_id=event_id)
        entries = copy.deepcopy(model.db.get_entries(event_id=event_id))

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
    with model.db.transaction():
        settings = model.db.get_series_settings()
        # build event list
        events = model.db.get_events()
        events = create_event_list(events=events)

        list_of_results = []
        organizers = []
        for i, event in enumerate(events):
            classes = model.db.get_classes(event_id=event.id)
            entries = model.db.get_entries(event_id=event.id)
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
    event: Optional[EventType] = None
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in model.db.get_events():
            if event_key != "" and e.key == event_key:
                event = e
                break
        else:
            raise EventNotFoundError(f'Event for key "{event_key}" not found')

        _, entries, status = iof_result_list.parse_result_list(content)
        if status != ResultListStatus.DELTA:
            model.db.delete_entries(event_id=event.id)
            model.db.delete_classes(event_id=event.id)
        model.db.import_entries(event_id=event.id, entries=entries)

    if event:
        cached_result.clear_cache(event_id=event.id)

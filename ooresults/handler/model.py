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
import datetime
import pathlib
import copy
import json
from typing import Optional
from typing import List
from typing import Dict
from typing import Tuple

import iso8601
import jsonschema

from ooresults.handler import build_results
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import TransactionMode
from ooresults.repo.class_params import ClassParams
from ooresults.repo import result_type
from ooresults.repo import start_type
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.series_type import Settings
from ooresults.websocket_server.websocket_server import WebSocketServer


websocket_server: Optional[WebSocketServer] = None
db: Optional[SqliteRepo] = None


data_path = (
    pathlib.Path(__file__).resolve().parent.parent / "schema" / "cardreader_log.json"
)
with open(data_path, "r") as f:
    schema_cardreader_log = json.loads(f.read())


def get_classes(event_id):
    with db.transaction():
        return db.get_classes(event_id=event_id)


def get_class(id):
    with db.transaction():
        return db.get_class(id=id)


def import_classes(event_id: int, classes: List[Dict]) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_classes = list(db.get_classes(event_id=event_id))
        for c in classes:
            for cl in existing_classes:
                if cl["name"] == c["name"]:
                    db.update_class(
                        id=cl["id"],
                        name=cl["name"],
                        short_name=c["short_name"]
                        if c.get("short_name", None) is not None
                        else cl["short_name"],
                        course_id=cl["course_id"],
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
    event_id,
    name,
    short_name: Optional[str],
    course_id: Optional[int],
    params: ClassParams,
):
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
            controls = db.get_course(id=course_id)[0]["controls"]
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
                    id=entry["id"],
                    chip=entry["chip"],
                    result=entry.result,
                    start_time=entry.start.start_time,
                )


def delete_classes(event_id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_classes(event_id=event_id)


def delete_class(id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_class(id=id)


def get_courses(event_id: int):
    with db.transaction():
        return db.get_courses(event_id=event_id)


def get_course(id):
    with db.transaction():
        return db.get_course(id=id)


def import_courses(
    event_id: int, courses: List[Dict], class_course: List[Dict]
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_courses = list(db.get_courses(event_id=event_id))
        for c in courses:
            for co in existing_courses:
                if co["name"] == c["name"]:
                    db.update_course(
                        id=co["id"],
                        name=co["name"],
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
        existing_classes = list(db.get_classes(event_id=event_id))
        existing_courses = list(db.get_courses(event_id=event_id))
        for i in class_course:
            for co in existing_courses:
                if co["name"] == i.get("course_name", None):
                    for cl in existing_classes:
                        if cl["name"] == i["class_name"]:
                            db.update_class(
                                id=cl["id"],
                                name=cl["name"],
                                short_name=cl["short_name"],
                                course_id=co["id"],
                                params=cl.params,
                            )
                            break
                    else:
                        id = db.add_class(
                            event_id=event_id,
                            name=i["class_name"],
                            short_name=None,
                            course_id=co["id"],
                            params=ClassParams(),
                        )
                        existing_classes.append({"id": id, "name": i["class_name"]})
                    break
            else:
                if i["course_name"] is None:
                    for cl in existing_classes:
                        if cl["name"] == i["class_name"]:
                            db.update_class(
                                id=cl["id"],
                                name=cl["name"],
                                short_name=cl["short_name"],
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
                        existing_classes.append({"id": id, "name": i["class_name"]})


def add_course(
    event_id: int,
    name: str,
    length: Optional[float],
    climb: Optional[float],
    controls: List[str],
):
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
                        id=entry["id"],
                        chip=entry["chip"],
                        result=entry.result,
                        start_time=entry.start.start_time,
                    )
                    break


def delete_courses(event_id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_courses(event_id=event_id)


def delete_course(id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_course(id=id)


def get_clubs():
    with db.transaction():
        return db.get_clubs()


def get_club(id):
    with db.transaction():
        return db.get_club(id=id)


def add_club(name):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_club(name=name)


def update_club(id, name):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_club(id=id, name=name)


def delete_club(id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_club(id=id)


def get_competitors():
    with db.transaction():
        return db.get_competitors()


def get_competitor(id):
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


def delete_competitor(id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_competitor(id=id)


def import_competitors(competitors):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.import_competitors(competitors)


def import_entries(event_id, entries):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.import_entries(event_id=event_id, entries=entries)


def get_entries(event_id):
    with db.transaction():
        return db.get_entries(event_id=event_id)


def get_entry(id):
    with db.transaction():
        return db.get_entry(id=id)


def add_entry(
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
) -> int:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        return db.add_entry(
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


def update_entry(
    id: int,
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
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
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


def add_entry_result(event_id, chip, start_time, result):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_entry_result(
            event_id=event_id,
            chip=chip,
            start_time=start_time,
            result=result,
        )


def update_entry_result(id, chip, start_time, result):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_entry_result(
            id=id,
            chip=chip,
            start_time=start_time,
            result=result,
        )


def delete_entries(event_id: int):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entries(event_id=event_id)


def delete_entry(id: int):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entry(id=id)


def get_events():
    with db.transaction():
        return db.get_events()


def get_event(id: int):
    with db.transaction():
        return db.get_event(id=id)


def add_event(
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: List[str] = [],
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.add_event(name, date, key, publish, series, fields)


def update_event(
    id: int,
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: List[str] = [],
) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_event(id, name, date, key, publish, series, fields)

    future = asyncio.run_coroutine_threadsafe(
        coro=websocket_server.handler.update_event(
            {"id": id, "name": name, "date": date}
        ),
        loop=websocket_server.loop,
    )
    future.result()


def delete_event(id):
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.delete_entries(event_id=id)
        db.delete_classes(event_id=id)
        db.delete_courses(event_id=id)
        db.delete_event(id)


def parse_cardreader_log(item: Dict) -> Dict:
    #
    # returns a dict consisting of:
    #
    # 'entryType': str,
    # 'entryTime': datetime.dateime,
    # 'controlCard': Optional[str],
    # 'result' : Optional[result_type.PersonRaceResult]
    #
    jsonschema.validate(item, schema_cardreader_log)
    d = {
        "entryType": item["entryType"],
        "entryTime": iso8601.parse_date(item["entryTime"]),
        "controlCard": item.get("controlCard", None),
        "result": None,
    }

    if d["entryType"] == "cardRead":
        result = result_type.PersonRaceResult(status=ResultStatus.FINISHED)
        if item.get("clearTime", None) is not None:
            result.punched_clear_time = iso8601.parse_date(item["clearTime"])
        if item.get("checkTime", None) is not None:
            result.punched_check_time = iso8601.parse_date(item["checkTime"])
        if item.get("startTime", None) is not None:
            result.punched_start_time = iso8601.parse_date(item["startTime"])
        if item.get("finishTime", None) is not None:
            result.punched_finish_time = iso8601.parse_date(item["finishTime"])
        result.start_time = result.punched_start_time
        result.finish_time = result.punched_finish_time
        for p in item["punches"]:
            result.split_times.append(
                result_type.SplitTime(
                    control_code=p["controlCode"],
                    punch_time=iso8601.parse_date(p["punchTime"]),
                    status="Additional",
                )
            )
        d["result"] = result

    return d


def store_cardreader_result(event_key: str, item: Dict) -> Tuple[str, Dict, Dict]:
    def missing_controls(result: result_type.PersonRaceResult) -> List[str]:
        if result.finish_time is None:
            return ["FINISH"]
        if result.start_time is None:
            return ["START"]
        controls = []
        for sp in result.split_times:
            if sp.status == "Missing":
                controls.append(sp.control_code)
        return controls

    with db.transaction(mode=TransactionMode.IMMEDIATE):
        for e in db.get_events():
            if event_key != "" and e.key == event_key:
                event = e
                break
        else:
            raise EventNotFoundError(f'Event for key "{event_key}" not found')

        if item["entryType"] == "cardRead":
            result = item["result"]

            entries = db.get_entries(event_id=event.id)
            entries_controlcard = [e for e in entries if e.chip == item["controlCard"]]
            assigned_entries = [e for e in entries_controlcard if e.class_ is not None]
            unassigned_entries = [e for e in entries_controlcard if e.class_ is None]

            for entry in assigned_entries:
                r = entry["result"]
                if r is not None and r.same_punches(other=result):
                    # result exists and is assigned to a competitor => nothing to do
                    res = {
                        "entryTime": item["entryTime"],
                        "eventId": event.id,
                        "controlCard": entry["chip"],
                        "firstName": entry["first_name"],
                        "lastName": entry["last_name"],
                        "club": entry["club"],
                        "class": entry["class_"],
                        "status": r["status"],
                        "time": r.extensions.get("running_time", r["time"]),
                        "error": None,
                        "missingControls": missing_controls(result=r),
                    }
                    break
            else:
                # check if result is already read out
                unassigned_entry = None
                for entry in unassigned_entries:
                    if entry["result"].same_punches(other=result):
                        unassigned_entry = entry
                        break

                # result can be assigned to an entry if
                #   (1) there is exactly one entry without result
                #   (2) there is no unassigned entry or one unassigned entry with same result
                if (
                    len(assigned_entries) == 1
                    and not assigned_entries[0]["result"].has_punches()
                    and (
                        len(unassigned_entries) == 0
                        or len(unassigned_entries) == 1
                        and unassigned_entries[0]["result"].same_punches(other=result)
                    )
                ):
                    entry = assigned_entries[0]
                    try:
                        class_ = db.get_class(id=entry["class_id"])[0]
                        course_id = class_["course_id"]
                        class_params = class_["params"]
                        controls = db.get_course(id=course_id)[0]["controls"]
                    except:
                        class_params = ClassParams()
                        controls = []

                    result.compute_result(
                        controls=controls,
                        class_params=class_params,
                        start_time=entry.start.start_time,
                        year=int(entry.get("year", None))
                        if entry.get("year", None) is not None
                        else None,
                        gender=entry.get("gender", None),
                    )
                    db.update_entry_result(
                        id=entry["id"],
                        chip=entry["chip"],
                        result=result,
                        start_time=entry["start"].start_time,
                    )
                    res = {
                        "entryTime": item["entryTime"],
                        "eventId": event.id,
                        "controlCard": entry["chip"],
                        "firstName": entry["first_name"],
                        "lastName": entry["last_name"],
                        "club": entry["club"],
                        "class": entry["class_"],
                        "status": result["status"],
                        "time": result.extensions.get("running_time", result["time"]),
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
                            chip=item["controlCard"],
                            result=result,
                            start_time=None,
                        )
                    res = {
                        "entryTime": item["entryTime"],
                        "eventId": event.id,
                        "controlCard": item["controlCard"],
                        "firstName": None,
                        "lastName": None,
                        "club": None,
                        "class": None,
                        "status": result["status"],
                        "time": None,
                    }
                    if len(assigned_entries) == 0:
                        res["error"] = "Control card unknown"
                    elif len(assigned_entries) >= 2:
                        res["error"] = "There are several entries for this card"
                    else:
                        res["error"] = "There are other results for this card"

        elif item["entryType"] == "cardInserted":
            res = {"eventId": event.id, "controlCard": item["controlCard"]}
        else:
            res = {"eventId": event.id}

    return item["entryType"], event, res


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
) -> None:
    #
    # result_id == -1: remove result from entry (store as pseudy result)
    #

    with db.transaction(mode=TransactionMode.IMMEDIATE):

        def store_result_as_new_entry(entry) -> None:
            result = entry.result
            result.status = ResultStatus.FINISHED
            result.split_times = [
                s for s in result.split_times if s.status != "Missing"
            ]
            for s in result.split_times:
                s.status = "Additional"
                if result.start_time is None:
                    s.time = None
            db.add_entry_result(
                event_id=entry.event_id,
                chip=entry.chip,
                result=result,
                start_time=None,
            )

        if id is None:
            entry = {
                "result": result_type.PersonRaceResult(),
                "start": start_type.PersonRaceStart(),
            }
            entry["id"] = db.add_entry(
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
        else:
            entry = db.get_entry(id=id)[0]
            if result_id is not None and entry.result.has_punches():
                store_result_as_new_entry(entry=entry)

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
            if result_id == -1:
                # remove result
                db.update_entry_result(
                    id=id,
                    chip=chip,
                    result=result_type.PersonRaceResult(),
                    start_time=start_time,
                )

        if result_id is not None and result_id != -1:
            # compute new result
            result_entry = db.get_entry(id=result_id)[0]
            try:
                class_ = db.get_class(id=class_id)[0]
                course_id = class_["course_id"]
                class_params = class_["params"]
                controls = db.get_course(id=course_id)[0]["controls"]
            except:
                class_params = ClassParams()
                controls = []

            result_entry.result.compute_result(
                controls=controls,
                class_params=class_params,
                start_time=start_time,
                year=year,
                gender=gender if gender != "" else None,
            )
            db.update_entry_result(
                id=entry["id"],
                chip=result_entry["chip"],
                result=result_entry.result,
                start_time=start_time,
            )
            db.delete_entry(id=result_entry["id"])

        elif id is not None and (
            class_id != entry.class_ or start_time != entry["start"].start_time
        ):
            # compute new result
            result_entry = db.get_entry(id=id)[0]
            if result_entry.result.has_punches():
                try:
                    class_ = db.get_class(id=class_id)[0]
                    course_id = class_["course_id"]
                    class_params = class_["params"]
                    controls = db.get_course(id=course_id)[0]["controls"]
                except:
                    class_params = ClassParams()
                    controls = []

                result_entry.result.compute_result(
                    controls=controls,
                    class_params=class_params,
                    start_time=start_time,
                    year=year,
                    gender=gender if gender != "" else None,
                )
                db.update_entry_result(
                    id=entry["id"],
                    chip=result_entry["chip"],
                    result=result_entry.result,
                    start_time=start_time,
                )


def get_series_settings() -> Settings:
    with db.transaction():
        return db.get_series_settings()


def update_series_settings(settings: Settings) -> None:
    with db.transaction(mode=TransactionMode.IMMEDIATE):
        db.update_series_settings(settings=settings)


def event_class_results(event_id: int) -> Tuple[Dict, List[Tuple[Dict, List[Dict]]]]:
    with db.transaction():
        event = list(db.get_event(id=event_id))
        event = event[0] if event != [] else {}

        classes = list(db.get_classes(event_id=event_id))
        entry_list = list(db.get_entries(event_id=event_id))

    class_results = build_results.build_results(
        classes=classes,
        results=copy.deepcopy(entry_list),
    )
    return event, class_results


def create_event_list(events):
    # filter list
    e_list = [e for e in events if e.series is not None]
    # sort list
    e_list.sort(key=lambda e: e.series)
    e_list.sort(key=lambda e: e.date)
    return e_list


def build_series_result():
    with db.transaction():
        settings = db.get_series_settings()
        # build event list
        events = list(db.get_events())
        events = create_event_list(events=events)

        list_of_results = []
        organizers = []
        for i, event in enumerate(events):
            classes = list(db.get_classes(event_id=event.id))
            entry_list = list(db.get_entries(event_id=event.id))
            class_results = build_results.build_results(
                classes=classes,
                results=copy.deepcopy(entry_list),
            )
            list_of_results.append(class_results)
            organizers.append([e for e in entry_list if e.class_ == "Organizer"])

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

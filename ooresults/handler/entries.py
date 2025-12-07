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


import datetime
import io
import json
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import bottle
import tzlocal

from ooresults import model
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import ResultStatus
from ooresults.plugins import iof_entry_list
from ooresults.plugins import iof_result_list
from ooresults.plugins import oe12
from ooresults.plugins import oe2003
from ooresults.plugins.imports.entries import text
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import render


"""
Handler for the entry routes.

/entry/update
/entry/import
/entry/export
/entry/add
/entry/fill_edit_form
/entry/fill_competitors_form
/entry/fill_result_form
/entry/delete
/entry/splitTimes
/entry/editPunch
"""


def update(event_id: int, view: str = "entries"):
    entry_list = model.entries.get_entries(event_id=event_id)
    try:
        event = model.events.get_event(id=event_id)

        unassigned_results = 0
        for e in entry_list:
            if e.class_id is None:
                unassigned_results += 1

        if view == "entries":
            if entry_list[unassigned_results:]:
                view_entries_list = [("Entries", entry_list[unassigned_results:])]
            else:
                view_entries_list = []
        elif view == "classes":
            view_entries: defaultdict[str, List[EntryType]] = defaultdict(list)
            for e in entry_list[unassigned_results:]:
                view_entries[e.class_name].append(e)
            view_entries_list = list(view_entries.items())
            view_entries_list.sort(key=lambda e: e[0] if e[0] is not None else "")
        elif view == "clubs":
            view_entries: defaultdict[str, List[EntryType]] = defaultdict(list)
            for e in entry_list[unassigned_results:]:
                view_entries[e.club_name].append(e)
            view_entries_list = list(view_entries.items())
            view_entries_list.sort(key=lambda e: e[0] if e[0] is not None else "")
        elif view == "states":
            view_entries: defaultdict[ResultStatus, List[EntryType]] = defaultdict(list)
            for e in entry_list[unassigned_results:]:
                view_entries[e.result.status].append(e)
            view_entries_list = list(view_entries.items())
            f_order = {
                ResultStatus.INACTIVE: 0,
                ResultStatus.ACTIVE: 1,
                ResultStatus.FINISHED: 2,
                ResultStatus.OK: 3,
                ResultStatus.MISSING_PUNCH: 4,
                ResultStatus.DID_NOT_FINISH: 5,
                ResultStatus.OVER_TIME: 6,
                ResultStatus.DISQUALIFIED: 7,
                ResultStatus.DID_NOT_START: 8,
            }
            view_entries_list.sort(key=lambda e: f_order[e[0]])
            f_name = {
                ResultStatus.INACTIVE: "Registered",
                ResultStatus.ACTIVE: "Started",
                ResultStatus.FINISHED: "Finished",
                ResultStatus.OK: "OK",
                ResultStatus.MISSING_PUNCH: "Missing punch",
                ResultStatus.DID_NOT_FINISH: "Did not finish",
                ResultStatus.OVER_TIME: "Over time",
                ResultStatus.DISQUALIFIED: "Disqualified",
                ResultStatus.DID_NOT_START: "Did not start",
            }
            view_entries_list = [(f_name[v[0]], v[1]) for v in view_entries_list]
        # add unassigned results
        if unassigned_results > 0:
            unassigned_list = [("Unassigned results", entry_list[:unassigned_results])]
        else:
            unassigned_list = []
        return render.entries_table(
            event=event,
            view=view,
            view_entries_list=unassigned_list + view_entries_list,
        )
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")


@bottle.post("/entry/update")
def post_update():
    """Update data"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    return update(event_id=event_id, view=data.view)


@bottle.post("/entry/import")
def post_import():
    """Import entries"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.entr_import == "entr.import.1":
            with io.BytesIO() as buffer:
                bottle.request.files.browse1.save(buffer)
                _, entries = iof_entry_list.parse_entry_list(content=buffer.getvalue())
        elif data.entr_import == "entr.import.2":
            with io.BytesIO() as buffer:
                bottle.request.files.browse2.save(buffer)
                _, entries, _ = iof_result_list.parse_result_list(
                    content=buffer.getvalue()
                )
        elif data.entr_import == "entr.import.3":
            event = model.events.get_event(id=event_id)
            with io.BytesIO() as buffer:
                bottle.request.files.browse3.save(buffer)
                entries = oe2003.parse(content=buffer.getvalue())

            tz = tzlocal.get_localzone()
            for e in entries:
                start_time = e["start"].start_time
                if start_time is not None:
                    e["start"].start_time = datetime.datetime.combine(
                        event.date, start_time.time(), tzinfo=tz
                    )
                    print("StartTime(start):", e["start"].start_time)
                start_time = e["result"].start_time
                if start_time is not None:
                    e["result"].start_time = datetime.datetime.combine(
                        event.date, start_time.time(), tzinfo=tz
                    )
                    e["result"].punched_start_time = e["result"].start_time
                    print("StartTime(result):", e["result"].start_time)
                finish_time = e["result"].finish_time
                if finish_time is not None:
                    e["result"].finish_time = datetime.datetime.combine(
                        event.date, finish_time.time(), tzinfo=tz
                    )
                    e["result"].punched_finish_time = e["result"].finish_time
                    print("FinishTime(result):", e["result"].finish_time)
                for i in e["result"].split_times:
                    if i.punch_time is not None:
                        i.punch_time = datetime.datetime.combine(
                            event.date, i.punch_time.time(), tzinfo=tz
                        )

        elif data.entr_import == "entr.import.4":
            with io.BytesIO() as buffer:
                bottle.request.files.browse4.save(buffer)
                entries = text.parse(content=buffer.getvalue())
        else:
            return bottle.HTTPResponse(status=409, body="Internal server error")

        # import only the first entry of the entries with same last and first name
        entries_1: List[Dict] = []
        names_1: Set[Tuple[str, str]] = set()
        names_2: Set[Tuple[str, str]] = set()
        for e in entries:
            name = (e["last_name"], e["first_name"])
            if name in names_1:
                names_2.add(name)
            else:
                names_1.add(name)
                entries_1.append(e)

        model.entries.import_entries(event_id=event_id, entries=entries_1)

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")

    answer = {"table": update(event_id=event_id, view=data.view)}
    if names_2:
        answer["status"] = render.entries_import_status(
            number_of_imported_entries=len(entries_1),
            number_of_entries=len(entries),
            names=names_2,
        )
    return json.dumps(answer)


@bottle.post("/entry/export")
def post_export():
    """Export entries"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    try:
        if data.entr_export == "entr.export.1":
            entry_list = model.entries.get_entries(event_id=event_id)
            event = model.events.get_event(id=event_id)
            content = iof_entry_list.create_entry_list(event, entry_list)
        elif data.entr_export == "entr.export.2":
            event, class_results = model.results.event_class_results(event_id=event_id)
            content = iof_result_list.create_result_list(event, class_results)
        elif data.entr_export == "entr.export.3":
            event, class_results = model.results.results_for_splitsbrowser(
                event_id=event_id
            )
            content = iof_result_list.create_result_list(event, class_results)
        elif data.entr_export == "entr.export.4":
            class_list = model.classes.get_classes(event_id=event_id)
            entry_list = model.entries.get_entries(event_id=event_id)
            content = oe2003.create(entry_list, class_list)
        elif data.entr_export == "entr.export.5":
            class_list = model.classes.get_classes(event_id=event_id)
            entry_list = model.entries.get_entries(event_id=event_id)
            content = oe12.create(entry_list, class_list)

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")

    return content


def parse_start_time(
    item: str, event_date: datetime.date
) -> Optional[datetime.datetime]:
    if item != "":
        format = "%H:%M:%S" if item.count(":") == 2 else "%M:%S"
        tz = tzlocal.get_localzone()
        dt = datetime.datetime.combine(
            date=event_date,
            time=datetime.datetime.strptime(item, format).time(),
            tzinfo=tz,
        )
        print(">>> ", dt)
        return dt
    else:
        return None


@bottle.post("/entry/add")
def post_add():
    """Add or edit entry"""
    try:
        data = bottle.request.forms
        print({key: value for key, value in data.items()})
        event_id = int(data.event_id) if data.event_id != "" else -1
        event = model.events.get_event(id=event_id)

        entered_start_time = parse_start_time(data.start_time, event.date)

        fields = {}
        for i in range(len(event.fields)):
            name = "f" + str(i)
            if name in data:
                fields[i] = data[name]

        model.entries.add_or_update_entry(
            id=int(data.id) if data.id != "" else None,
            event_id=event_id,
            competitor_id=(
                int(data.competitor_id) if data.competitor_id != "" else None
            ),
            first_name=data.first_name,
            last_name=data.last_name,
            gender=data.gender,
            year=int(data.year) if data.year != "" else None,
            class_id=int(data.class_id),
            club_id=int(data.club_id) if data.club_id != "" else None,
            not_competing="not_competing" in data and data.not_competing == "true",
            chip=data.chip.strip(),
            fields=fields,
            status=ResultStatus(int(data.status)),
            start_time=entered_start_time,
            result_id=int(data.result) if data.get("result", "") else None,
        )

    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except ConstraintError as e:
        return bottle.HTTPResponse(status=409, body=str(e))
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Entry deleted")

    return update(event_id=event_id, view=data.view)


def collect_unassigned_si_results(entries: List[EntryType]) -> Dict[int, str]:
    unassigned_results = {}
    for e in entries:
        if e.last_name is None:
            last_punch = e.result.finish_time
            if last_punch is None:
                for s in reversed(e.result.split_times):
                    if s.punch_time is not None:
                        last_punch = s.punch_time
                        break
                else:
                    if e.result.start_time is not None:
                        last_punch = e.result.start_time

            if last_punch is None:
                punch_time = "--:--:--"
            else:
                punch_time = last_punch.strftime("%H:%M:%S")
            unassigned_results[e.id] = f"{punch_time}   --   {e.chip}"

    return unassigned_results


@bottle.post("/entry/fill_edit_form")
def post_fill_edit_form():
    """Query data to fill add or edit form"""
    try:
        data = bottle.request.forms
        event_id = int(data.event_id) if data.event_id != "" else -1
        event = model.events.get_event(id=event_id)

        if data.id == "":
            entry = None
        else:
            entry = model.entries.get_entry(int(data.id))

        entries = model.entries.get_entries(event_id=event_id)
        unassigned_results = collect_unassigned_si_results(entries=entries)

        classes = model.classes.get_classes(event_id=event_id)
        clubs = model.clubs.get_clubs()
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Entry deleted")

    return render.add_entry(
        entry=entry,
        classes=classes,
        clubs=clubs,
        unassigned_results=unassigned_results,
        event_fields=event.fields,
    )


@bottle.post("/entry/fill_competitors_form")
def post_fill_competitors_form():
    """Query data to fill add or edit form"""
    competitors = model.competitors.get_competitors()

    return render.add_entry_competitors(competitors=competitors)


@bottle.post("/entry/fill_result_form")
def post_fill_result_form():
    """Query data to fill result form"""
    data = bottle.request.forms
    try:
        entry = model.entries.get_entry(int(data.id))
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Entry deleted")

    return render.add_entry_result(entry=entry)


@bottle.post("/entry/delete")
def post_delete():
    """Delete entry"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    model.entries.delete_entry(int(data.id))
    return update(event_id=event_id, view=data.view)


@bottle.post("/entry/splitTimes")
def post_split_times():
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    return update(event_id=event_id, view=data.view)


@bottle.post("/entry/editPunch")
def post_edit_punch():
    """Change split times"""
    data = bottle.request.forms
    event_id = int(data.event_id) if data.event_id != "" else -1
    entry_id = int(data.entry_id) if data.entry_id != "" else -1

    if data.command not in ["entr_ep_del", "entr_ep_edit", "entr_ep_add"]:
        raise RuntimeError

    if data.selectedRow == "-1":
        selected_row = "START"
    elif data.selectedRow == "-2":
        selected_row = "FINISH"
    else:
        selected_row = int(data.selectedRow)

    punch_time = None
    if data.command != "entr_ep_del" and data.punch_time != "":
        punch_time = datetime.time.fromisoformat(data.punch_time)

    try:
        entry = model.entries.edit_entry_result(
            entry_id=entry_id,
            event_id=event_id,
            command=data.command,
            control=data.control,
            selected_row=selected_row,
            punch_time=punch_time,
        )
    except EventNotFoundError:
        return bottle.HTTPResponse(status=409, body="Event deleted")
    except KeyError:
        return bottle.HTTPResponse(status=409, body="Entry deleted")
    except RuntimeError:
        return bottle.HTTPResponse(status=409, body="Course data changed")

    return render.add_entry_result(entry=entry)

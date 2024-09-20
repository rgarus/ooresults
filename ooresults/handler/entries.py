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


import logging
import datetime
import pathlib
from typing import List
from typing import Dict
from typing import Optional

import tzlocal
import web

from ooresults.model import model
from ooresults.plugins.imports.entries import text
from ooresults.plugins import oe12
from ooresults.plugins import oe2003
from ooresults.plugins import iof_entry_list
from ooresults.plugins import iof_result_list
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import ConstraintError
from ooresults.utils.globals import t_globals


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals=t_globals)


def update(event_id: int):
    entry_list = model.get_entries(event_id=event_id)
    try:
        event = model.get_event(id=event_id)
        return render.entries_table(event, entry_list)
    except EventNotFoundError:
        raise web.conflict("Event deleted")
    except:
        logging.exception("Internal server error")
        raise


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        return update(event_id=event_id)


class Import:
    def POST(self):
        """Import entries"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.entr_import == "entr.import.1":
                _, entries = iof_entry_list.parse_entry_list(data.browse1)
                model.import_entries(event_id=event_id, entries=entries)
            elif data.entr_import == "entr.import.2":
                _, entries, _ = iof_result_list.parse_result_list(data.browse2)
                model.import_entries(event_id=event_id, entries=entries)
            elif data.entr_import == "entr.import.3":
                event = model.get_event(id=event_id)
                entries = oe2003.parse(content=data.browse3)

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

                model.import_entries(event_id=event_id, entries=entries)
            elif data.entr_import == "entr.import.4":
                entries = text.parse(content=data.browse4)
                model.import_entries(event_id=event_id, entries=entries)

        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except Exception as e:
            raise web.conflict(str(e))
        except:
            logging.exception("Internal server error")
            raise

        return update(event_id)


class Export:
    def POST(self):
        """Export entries"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            if data.entr_export == "entr.export.1":
                entry_list = model.get_entries(event_id=event_id)
                event = model.get_event(id=event_id)
                content = iof_entry_list.create_entry_list(event, entry_list)
            elif data.entr_export == "entr.export.2":
                event, class_results = model.event_class_results(event_id=event_id)
                content = iof_result_list.create_result_list(event, class_results)
            elif data.entr_export == "entr.export.3":
                event, class_results = model.results_for_splitsbrowser(
                    event_id=event_id
                )
                content = iof_result_list.create_result_list(event, class_results)
            elif data.entr_export == "entr.export.4":
                class_list = model.get_classes(event_id=event_id)
                entry_list = model.get_entries(event_id=event_id)
                content = oe2003.create(entry_list, class_list)
            elif data.entr_export == "entr.export.5":
                class_list = model.get_classes(event_id=event_id)
                entry_list = model.get_entries(event_id=event_id)
                content = oe12.create(entry_list, class_list)

        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except:
            logging.exception("Internal server error")
            raise

        return content


class Add:
    def parse_start_time(
        self, item: str, event_date: datetime.date
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

    def POST(self):
        """Add or edit entry"""
        try:
            data = web.input()
            print(data)
            event_id = int(data.event_id) if data.event_id != "" else -1
            event = model.get_event(id=event_id)

            entered_start_time = self.parse_start_time(data.start_time, event.date)

            fields = {}
            for i in range(len(event.fields)):
                name = "f" + str(i)
                if name in data:
                    fields[i] = data[name]

            model.add_or_update_entry(
                id=int(data.id) if data.id != "" else None,
                event_id=event_id,
                competitor_id=int(data.competitor_id)
                if data.competitor_id != ""
                else None,
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
            raise web.conflict("Event deleted")
        except ConstraintError as e:
            raise web.conflict(str(e))
        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return update(event_id)


class FillEditForm:
    def collect_not_assigned_si_results(self, entries) -> List[Dict]:
        results = []
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

                results.append({"key": e.id, "value": f"{punch_time}   --   {e.chip}"})
        return results

    def POST(self):
        """Query data to fill add or edit form"""
        try:
            data = web.input()
            event_id = int(data.event_id) if data.event_id != "" else -1
            event = model.get_event(id=event_id)

            results = []
            if data.id == "":
                entry = None
            else:
                entry = model.get_entry(int(data.id))
                if entry.result is not None and entry.result.has_punches():
                    results += [{"key": -1, "value": "Remove result"}]

            entries = model.get_entries(event_id=event_id)
            results += self.collect_not_assigned_si_results(entries)

            classes = model.get_classes(event_id=event_id)
            clubs = model.get_clubs()
        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return render.add_entry(entry, classes, clubs, results, event.fields)


class FillCompetitorsForm:
    def POST(self):
        """Query data to fill add or edit form"""
        data = web.input()
        competitors = model.get_competitors()

        return render.add_entry_competitors(competitors)


class FillResultForm:
    def POST(self):
        """Query data to fill result form"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        try:
            entry = model.get_entry(int(data.id))
        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except KeyError:
            raise web.conflict("Entry deleted")
        except:
            logging.exception("Internal server error")
            raise

        return render.add_entry_result(entry)


class Delete:
    def POST(self):
        """Delete entry"""
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        model.delete_entry(int(data.id))
        return update(event_id=event_id)


class SplitTimes:
    def POST(self):
        data = web.input()
        event_id = int(data.event_id) if data.event_id != "" else -1
        return update(event_id=event_id)


class EditPunch:
    def POST(self):
        """Change split times"""
        data = web.input()
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
            entry = model.edit_entry_result(
                entry_id=entry_id,
                event_id=event_id,
                command=data.command,
                control=data.control,
                selected_row=selected_row,
                punch_time=punch_time,
            )
        except EventNotFoundError:
            raise web.conflict("Event deleted")
        except KeyError:
            raise web.conflict("Entry deleted")
        except RuntimeError:
            raise web.conflict("Course data changed")
        except:
            logging.exception("Internal server error")
            raise

        return render.add_entry_result(entry)

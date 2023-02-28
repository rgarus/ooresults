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
import logging
import pathlib
import io
from decimal import Decimal

import web
import clevercsv as csv

from ooresults.handler import model
from ooresults.handler import results
from ooresults.repo import series_type
import ooresults.pdf.series


templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
render = web.template.render(templates, globals={"str": str})


def build_total_results(settings: series_type.Settings, list_of_results, organizers=[]):
    q = Decimal(10) ** -settings.decimal_places

    r = {}
    for i, class_results in enumerate(list_of_results):
        for class_, results in class_results:
            if class_.name == "Organizer":
                continue
            if class_.name not in r:
                r[class_.name] = {}
            for entry in results:
                # check if competitor has points
                if entry.get("points", None) is not None:
                    if (entry["last_name"], entry["first_name"]) not in r[class_.name]:
                        r[class_.name][(entry["last_name"], entry["first_name"])] = {
                            "last_name": entry["last_name"],
                            "first_name": entry["first_name"],
                            "year": entry.get("year", None),
                            "club": entry.get("club", None),
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }

                    p = Decimal(settings.maximum_points * entry["points"]).quantize(q)
                    r[class_.name][(entry["last_name"], entry["first_name"])]["races"][
                        i
                    ] = p
            # add organizers
            if len(organizers) > i:
                for entry in organizers[i]:
                    if (entry["last_name"], entry["first_name"]) not in r[class_.name]:
                        r[class_.name][(entry["last_name"], entry["first_name"])] = {
                            "last_name": entry["last_name"],
                            "first_name": entry["first_name"],
                            "year": entry.get("year", None),
                            "club": entry.get("club", None),
                            "sum": 0,
                            "races": {},
                            "organizer": {},
                        }
                    r[class_.name][(entry["last_name"], entry["first_name"])][
                        "organizer"
                    ][i] = 0

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


def create_event_list(events):
    # filter list
    e_list = [e for e in events if e.series is not None]
    # sort list
    e_list.sort(key=lambda e: e.series)
    e_list.sort(key=lambda e: e.date)
    return e_list


def build_result():
    settings = model.get_series_settings()
    # build event list
    events = list(model.get_events())
    events = create_event_list(events=events)

    list_of_results = []
    organizers = []
    for i, event in enumerate(events):
        classes = list(model.get_classes(event_id=event.id))
        entry_list = list(model.get_entries(event_id=event.id))
        class_results = results.build_results(
            classes=classes, results=copy.deepcopy(entry_list)
        )
        list_of_results.append(class_results)
        organizers.append([e for e in entry_list if e.class_ == "Organizer"])

    return (
        settings,
        events,
        build_total_results(
            settings=settings, list_of_results=list_of_results, organizers=organizers
        ),
    )


class Update:
    def POST(self):
        """Update data"""
        data = web.input()
        settings, events, results = build_result()
        return render.series_table(events, results)


class Settings:
    def POST(self):
        """Update seeries settings"""
        data = web.input()
        print(data)
        try:
            settings = series_type.Settings(
                name=data.name,
                nr_of_best_results=int(data.nr_of_best_results)
                if data.nr_of_best_results != ""
                else None,
                mode=data.mode,
                maximum_points=int(data.maximum_points),
                decimal_places=int(data.decimal_places),
            )
            model.update_series_settings(settings=settings)
        except Exception as e:
            raise web.internalerror(str(e))

        settings, events, results = build_result()
        return render.series_table(events, results)


class PdfResult:
    def POST(self):
        """Print results"""
        data = web.input()
        landscape = "ser_landscape" in data

        try:
            settings, events, results = build_result()
            content = ooresults.pdf.series.create_pdf(
                settings=settings, events=events, results=results, landscape=landscape
            )
            return content

        except KeyError:
            raise web.conflict("Internal error")
        except:
            logging.exception("Internal server error")
            raise


class CsvResult:
    def POST(self):
        """Export results as csv for creating diplomas"""
        data = web.input()
        try:
            settings, events, results = build_result()

            output = io.StringIO()
            writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

            # write header
            writer.writerow(
                [
                    "Kategorie",
                    "Pos",
                    "Pos_eng",
                    "Vorname",
                    "Nachname",
                    "Verein",
                    "Punkte",
                ]
            )

            for class_name, ranked_results in results:
                for result in ranked_results:
                    if result.get("rank", None) is not None:
                        rank = str(result.get("rank", None))
                        if rank == "1":
                            rank_eng = rank + "st"
                        elif rank == "2":
                            rank_eng = rank + "nd"
                        elif rank == "3":
                            rank_eng = rank + "rd"
                        else:
                            rank_eng = rank + "th"
                        writer.writerow(
                            [
                                class_name,
                                rank,
                                rank_eng,
                                result.get("first_name", ""),
                                result.get("last_name", ""),
                                result.get("club", ""),
                                str(result.get("sum", None)),
                            ]
                        )

            content = output.getvalue()
            output.close()
            return content.encode(encoding="utf-8")

        except KeyError:
            raise web.conflict("Internal error")
        except:
            logging.exception("Internal server error")
            raise


class FillSettingsForm:
    def POST(self):
        """Query data to fill settings form"""
        settings = model.get_series_settings()
        return render.series_settings(settings)

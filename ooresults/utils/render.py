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


import pathlib
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from mako.template import Template

from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.series_type import PersonSeriesResult
from ooresults.otypes.series_type import Settings
from ooresults.websocket_server.streaming_status import Status


_templates = pathlib.Path(__file__).resolve().parent.parent / "templates"


def t(name: str):
    return Template(
        filename=str(_templates / name),
        default_filters=["f", "h"],
        imports=["from ooresults.utils.globals import format as f"],
    )


_si__si1_data = t("si/si1_data.html")
_si__si1_error = t("si/si1_error.html")
_si__si1_page = t("si/si1_page.html")
_si__si2_data = t("si/si2_data.html")
_si__si2_page = t("si/si2_page.html")
_add_class = t("add_class.html")
_add_club = t("add_club.html")
_add_competitor = t("add_competitor.html")
_add_course = t("add_course.html")
_add_entry = t("add_entry.html")
_add_entry_competitors = t("add_entry_competitors.html")
_add_entry_result = t("add_entry_result.html")
_add_event = t("add_event.html")
_base = t("base.html")
_classes_tab_content = t("classes_tab_content.html")
_classes_table = t("classes_table.html")
_clubs_tab_content = t("clubs_tab_content.html")
_clubs_table = t("clubs_table.html")
_competitors_tab_content = t("competitors_tab_content.html")
_competitors_table = t("competitors_table.html")
_courses_tab_content = t("courses_tab_content.html")
_courses_table = t("courses_table.html")
_demo_reader = t("demo_reader.html")
_entries_tab_content = t("entries_tab_content.html")
_entries_table = t("entries_table.html")
_events_tab_content = t("events_tab_content.html")
_events_table = t("events_table.html")
_main = t("main.html")
_results_tab_content = t("results_tab_content.html")
_results_table = t("results_table.html")
_root = t("root.html")
_select_event = t("select_event.html")
_series_settings = t("series_settings.html")
_series_tab_content = t("series_tab_content.html")
_series_table = t("series_table.html")
_unauthorized = t("unauthorized.html")


def si1_page(event_id: Optional[int], key: Optional[str]) -> str:
    return _si__si1_page.render(event_id=event_id, key=key)


def si1_data(message: Dict) -> str:
    return _si__si1_data.render(message=message)


def si1_error(message: Dict) -> str:
    return _si__si1_error.render(message=message)


def si2_page(event_id: Optional[int], key: Optional[str]) -> str:
    return _si__si2_page.render(event_id=event_id, key=key)


def si2_data(
    status: str,
    stream_status: Optional[Status],
    event: EventType,
    messages: List[Dict],
) -> str:
    return _si__si2_data.render(
        status=status, stream_status=stream_status, event=event, messages=messages
    )


def classes_table(event: Optional[EventType], classes: List[ClassInfoType]) -> str:
    return _classes_table.render(event=event, classes=classes)


def add_class(class_: Optional[ClassType], courses: List[CourseType]) -> str:
    return _add_class.render(class_=class_, courses=courses)


def clubs_table(clubs: List[ClubType]) -> str:
    return _clubs_table.render(clubs=clubs)


def add_club(club: Optional[ClubType]) -> str:
    return _add_club.render(club=club)


def competitors_table(competitors: List[CompetitorType]) -> str:
    return _competitors_table.render(competitors=competitors)


def add_competitor(competitor: Optional[CompetitorType], clubs: List[ClubType]) -> str:
    return _add_competitor.render(competitor=competitor, clubs=clubs)


def courses_table(event: Optional[EventType], courses: List[CourseType]) -> str:
    return _courses_table.render(event=event, courses=courses)


def add_course(course: Optional[CourseType]) -> str:
    return _add_course.render(course=course)


def entries_table(
    event: Optional[EventType],
    view: str,
    view_entries_list: List[Tuple[Optional[str], List[EntryType]]],
) -> str:
    return _entries_table.render(
        event=event, view=view, view_entries_list=view_entries_list
    )


def add_entry(
    entry: Optional[EntryType],
    classes: List[ClassType],
    clubs: List[ClubType],
    unassigned_results: Dict[int, str],
    event_fields: List[str],
) -> str:
    return _add_entry.render(
        entry=entry,
        classes=classes,
        clubs=clubs,
        unassigned_results=unassigned_results,
        event_fields=event_fields,
    )


def add_entry_competitors(competitors: List[CompetitorType]) -> str:
    return _add_entry_competitors.render(competitors=competitors)


def add_entry_result(entry: EntryType) -> str:
    return _add_entry_result.render(entry=entry)


def events_table(events: List[EventType]) -> str:
    return _events_table.render(events=events)


def add_event(event: Optional[EventType]) -> str:
    return _add_event.render(event=event)


def results_table(
    event: EventType,
    class_results: List[Tuple[ClassInfoType, List[RankedEntryType]]],
) -> str:
    return _results_table.render(event=event, class_results=class_results)


def series_table(
    events: List[EventType], results: List[Tuple[str, List[PersonSeriesResult]]]
) -> str:
    return _series_table.render(events=events, results=results)


def series_settings(settings: Optional[Settings]) -> str:
    return _series_settings.render(settings=settings)


def unauthorized() -> str:
    return _unauthorized.render()


def demo_reader() -> str:
    return _demo_reader.render()


def root(results_table: Optional[str]) -> str:
    return _root.render(results_table=results_table)


def main(events: List[EventType]) -> str:
    events_table = _events_table.render(events=events)
    events_tab = _events_tab_content.render(events_table=events_table)
    entries_table = _entries_table.render(
        event=None, view="entries", view_entries_list=[]
    )
    entries_tab = _entries_tab_content.render(entries_table=entries_table)
    classes_table = _classes_table.render(event=None, classes=[])
    classes_tab = _classes_tab_content.render(classes_table=classes_table)
    courses_table = _courses_table.render(event=None, courses=[])
    courses_tab = _courses_tab_content.render(courses_table=courses_table)
    results_table = _results_table.render(event=None, class_results=[])
    results_tab = _results_tab_content.render(results=results_table)
    series_table = _series_table.render(events=[], results=[])
    series_tab = _series_tab_content.render(results=series_table)
    competitors_table = _competitors_table.render(competitors=[])
    competitors_tab = _competitors_tab_content.render(
        competitors_table=competitors_table
    )
    clubs_table = _clubs_table.render(clubs=[])
    clubs_tab = _clubs_tab_content.render(clubs_table=clubs_table)

    page = _main.render(
        events_tab_content=events_tab,
        entries_tab_content=entries_tab,
        classes_tab_content=classes_tab,
        courses_tab_content=courses_tab,
        results_tab_content=results_tab,
        series_tab_content=series_tab,
        competitors_tab_content=competitors_tab,
        clubs_tab_content=clubs_tab,
    )
    return _base.render(page=page)

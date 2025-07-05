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

import web

from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.class_type import ClassParams
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.result_type import SpStatus
from ooresults.otypes.series_type import PersonSeriesResult
from ooresults.otypes.series_type import Settings
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.utils.globals import MAP_STATUS
from ooresults.utils.globals import STREAMING_STATUS
from ooresults.utils.globals import build_columns
from ooresults.utils.globals import minutes_seconds
from ooresults.utils.globals import streaming_status_ok
from ooresults.utils.rental_cards import format_card
from ooresults.websocket_server.streaming_status import Status
from ooresults.websocket_server.streaming_status import StreamingStatus


web.config.debug = False


EXPERIMENTAL = False


t_globals = {
    "str": str,
    "round": round,
    "ClassParams": ClassParams,
    "ResultStatus": ResultStatus,
    "SplitTime": SplitTime,
    "SpStatus": SpStatus,
    "PersonRaceResult": PersonRaceResult,
    "PersonRaceStart": PersonRaceStart,
    "MAP_STATUS": MAP_STATUS,
    "STREAMING_STATUS": STREAMING_STATUS,
    "streaming_status_ok": streaming_status_ok,
    "EXPERIMENTAL": EXPERIMENTAL,
    "build_columns": build_columns,
    "minutes_seconds": minutes_seconds,
    "format_card": format_card,
}


_templates = pathlib.Path(__file__).resolve().parent.parent / "templates"
_render_base = web.template.render(_templates, base="base", globals={"str": str})
_render = web.template.render(_templates, globals=t_globals)


def si1_page(id: Optional[int], key: Optional[str]) -> str:
    return str(_render.si.si1_page(id=id, key=key))


def si1_data(message: Dict) -> str:
    return str(_render.si.si1_data(message=message))


def si1_error(message: Dict) -> str:
    return str(_render.si.si1_error(message=message))


def si2_page(id: Optional[int], key: Optional[str]) -> str:
    return str(_render.si.si2_page(id=id, key=key))


def si2_data(
    status: Status,
    stream_status: Optional[StreamingStatus],
    event: EventType,
    messages: List[Dict],
) -> str:
    return str(
        _render.si.si2_data(
            status=status, stream_status=stream_status, event=event, messages=messages
        )
    )


def classes_table(event: Optional[EventType], classes: List[ClassInfoType]) -> str:
    return str(_render.classes_table(event=event, classes=classes))


def add_class(class_: Optional[ClassType], courses: List[CourseType]) -> str:
    return str(_render.add_class(class_=class_, courses=courses))


def clubs_table(clubs: List[ClubType]) -> str:
    return str(_render.clubs_table(clubs=clubs))


def add_club(club: Optional[ClubType]) -> str:
    return str(_render.add_club(club=club))


def competitors_table(competitors: List[CompetitorType]) -> str:
    return str(_render.competitors_table(competitors=competitors))


def add_competitor(competitor: Optional[CompetitorType], clubs: List[ClubType]) -> str:
    return str(_render.add_competitor(competitor=competitor, clubs=clubs))


def courses_table(event: Optional[EventType], courses: List[CourseType]) -> str:
    return str(_render.courses_table(event=event, courses=courses))


def add_course(course: Optional[CourseType]) -> str:
    return str(_render.add_course(course=course))


def entries_table(
    event: Optional[EventType],
    view: str,
    view_entries_list: List[Tuple[Optional[str], List[EntryType]]],
) -> str:
    return str(
        _render.entries_table(
            event=event, view=view, view_entries_list=view_entries_list
        )
    )


def add_entry(
    entry: Optional[EntryType],
    classes: List[ClassType],
    clubs: List[ClubType],
    unassigned_results: Dict[int, str],
    event_fields: List[str],
) -> str:
    return str(
        _render.add_entry(
            entry=entry,
            classes=classes,
            clubs=clubs,
            unassigned_results=unassigned_results,
            event_fields=event_fields,
        )
    )


def add_entry_competitors(competitors: List[CompetitorType]) -> str:
    return str(_render.add_entry_competitors(competitors=competitors))


def add_entry_result(entry: EntryType) -> str:
    return str(_render.add_entry_result(entry=entry))


def events_table(events: List[EventType]) -> str:
    return str(_render.events_table(events=events))


def add_event(event: Optional[EventType]) -> str:
    return str(_render.add_event(event=event))


def results_table(
    event: EventType,
    class_results: List[Tuple[ClassInfoType, List[RankedEntryType]]],
) -> str:
    return str(_render.results_table(event=event, class_results=class_results))


def series_table(
    events: List[EventType], results: List[Tuple[str, List[PersonSeriesResult]]]
) -> str:
    return str(_render.series_table(events=events, results=results))


def series_settings(settings: Optional[Settings]) -> str:
    return str(_render.series_settings(settings=settings))


def unauthorized() -> str:
    return str(_render.unauthorized())


def demo_reader() -> str:
    return str(_render.demo_reader())


def root(results_table: Optional[str]) -> str:
    return str(_render.root(results_table=results_table))


def main(events: List[EventType]) -> str:
    events_table = _render.events_table(events=events)
    events_tab_content = _render.events_tab_content(events_table)
    entries_table = _render.entries_table(None, "entries", [])
    entries_tab_content = _render.entries_tab_content(entries_table)
    classes_table = _render.classes_table(None, [])
    classes_tab_content = _render.classes_tab_content(classes_table)
    courses_table = _render.courses_table(None, [])
    courses_tab_content = _render.courses_tab_content(courses_table)
    results_table = _render.results_table(None, [])
    results_tab_content = _render.results_tab_content(results_table)
    series_table = _render.series_table([], [])
    series_tab_content = _render.series_tab_content(series_table)
    competitors_table = _render.competitors_table([])
    competitors_tab_content = _render.competitors_tab_content(competitors_table)
    clubs_table = _render.clubs_table([])
    clubs_tab_content = _render.clubs_tab_content(clubs_table)
    return str(
        _render_base.main(
            events_tab_content,
            entries_tab_content,
            classes_tab_content,
            courses_tab_content,
            results_tab_content,
            series_tab_content,
            competitors_tab_content,
            clubs_tab_content,
        )
    )

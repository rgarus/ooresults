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
import pathlib
from datetime import timezone
from typing import List

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.utils.globals import t_globals


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def event() -> EventType:
    return EventType(
        id=3,
        name="Test-Lauf 1",
        date=datetime.date(
            year=2023,
            month=12,
            day=29,
        ),
        key=None,
        publish=False,
        series=None,
        fields=[],
    )


def headers(table: etree.Element) -> List[str]:
    headers = []
    for h in table.findall(path=".//thead//tr//th"):
        headers.append(h.text)
    return headers


def rows(table: etree.Element) -> List[List[str]]:
    rows = []
    for row in table.findall(path=".//tbody//tr"):
        content = []
        for cell in row.xpath(_path=".//th | .//td"):
            content.append(cell.text)
        rows.append(content)
    return rows


def test_entries_table_with_no_entries(render, event: EventType):
    view_entries_list = []
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=view_entries_list
            )
        )
    )

    table = html.find(".//table[@id='entr.table']")
    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "\xa0\xa0NC\xa0\xa0",
        "Start",
        "Time",
        "Status",
    ]
    assert rows(table) == []


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
F1 = datetime.datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)


def test_entries_table_with_several_entries(render, event: EventType):
    entries = [
        EntryType(
            id=112,
            event_id=event.id,
            competitor_id=122,
            first_name="Barbara",
            last_name="Merkel",
            gender=None,
            year=None,
            class_id=131,
            class_name="Elite F",
            not_competing=False,
            chip=None,
            fields={},
            result=PersonRaceResult(),
            start=PersonRaceStart(start_time=S1),
            club_id=None,
            club_name=None,
        ),
        EntryType(
            id=113,
            event_id=event.id,
            competitor_id=123,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=131,
            class_name="Elite F",
            not_competing=False,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                start_time=S1,
                finish_time=F1,
                punched_start_time=S1,
                punched_finish_time=F1,
                si_punched_start_time=S1,
                si_punched_finish_time=F1,
                status=ResultStatus.OK,
                time=t(S1, F1),
                split_times=[],
            ),
            start=PersonRaceStart(),
            club_id=145,
            club_name="OL Bundestag",
        ),
        EntryType(
            id=114,
            event_id=event.id,
            competitor_id=124,
            first_name="Manfred",
            last_name="Merkel",
            gender="M",
            year=1959,
            class_id=132,
            class_name="Elite M",
            not_competing=True,
            chip="4748496",
            fields={},
            result=PersonRaceResult(
                start_time=S1,
                finish_time=F1,
                punched_start_time=S1,
                punched_finish_time=F1,
                si_punched_start_time=S1,
                si_punched_finish_time=F1,
                status=ResultStatus.MISSING_PUNCH,
                time=t(S1, F1),
                split_times=[],
            ),
            start=PersonRaceStart(),
            club_id=145,
            club_name="OL Bundestag",
        ),
    ]
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    table = html.find(".//table[@id='entr.table']")
    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "\xa0\xa0NC\xa0\xa0",
        "Start",
        "Time",
        "Status",
    ]

    assert rows(table) == [
        [
            "Entries\xa0\xa0(3)",
        ],
        [
            "Barbara",
            "Merkel",
            None,
            None,
            None,
            None,
            "Elite F",
            None,
            "12:38:59",
            None,
            None,
        ],
        [
            "Angela",
            "Merkel",
            "F",
            "1957",
            "4748495",
            "OL Bundestag",
            "Elite F",
            None,
            None,
            "0:08",
            "OK",
        ],
        [
            "Manfred",
            "Merkel",
            "M",
            "1959",
            "4748496",
            "OL Bundestag",
            "Elite M",
            "X",
            None,
            "0:08",
            "MP",
        ],
    ]


def test_entries_table_with_fields(render):
    event = EventType(
        id=3,
        name="Test-Lauf 1",
        date=datetime.date(
            year=2023,
            month=12,
            day=29,
        ),
        key=None,
        publish=False,
        series=None,
        fields=["Start number", "Region"],
    )

    entries = [
        EntryType(
            id=112,
            event_id=event.id,
            competitor_id=122,
            first_name="Barbara",
            last_name="Merkel",
            gender=None,
            year=None,
            class_id=131,
            class_name="Elite F",
            not_competing=False,
            chip=None,
            fields={0: "121", 1: "Bayern"},
            result=PersonRaceResult(),
            start=PersonRaceStart(start_time=S1),
            club_id=None,
            club_name=None,
        ),
    ]
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    table = html.find(".//table[@id='entr.table']")
    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    assert headers(table) == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "\xa0\xa0NC\xa0\xa0",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]
    assert rows(table) == [
        [
            "Entries\xa0\xa0(1)",
        ],
        [
            "Barbara",
            "Merkel",
            None,
            None,
            None,
            None,
            "Elite F",
            None,
            "121",
            "Bayern",
            "12:38:59",
            None,
            None,
        ],
    ]

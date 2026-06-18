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
from datetime import timezone
from typing import Optional

import pytest

from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import ResultStatus
from ooresults.utils import render
from tests.templates.conftest import Html


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


@pytest.fixture()
def class_info_1(event: EventType) -> ClassInfoType:
    return ClassInfoType(
        id=12,
        name="Elite Women",
        short_name="Elite F",
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


@pytest.fixture()
def class_info_2(event: EventType) -> ClassInfoType:
    return ClassInfoType(
        id=12,
        name="Elite Men",
        short_name="Elite M",
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


@pytest.fixture()
def entry_1(event: EventType) -> EntryType:
    return EntryType(
        id=789,
        event_id=event.id,
        competitor_id=123,
        first_name="Angela",
        last_name="Merkel",
    )


@pytest.fixture()
def entry_2(event: EventType) -> EntryType:
    return EntryType(
        id=790,
        event_id=event.id,
        competitor_id=124,
        first_name="Barbara",
        last_name="Merkel",
    )


@pytest.fixture()
def entry_3(event: EventType) -> EntryType:
    return EntryType(
        id=791,
        event_id=event.id,
        competitor_id=125,
        first_name="Bernd",
        last_name="Derkel",
    )


TABLE_ID = "entr.table"


def test_class_results_list_is_empty(event: EventType) -> None:
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[],
            columns=set(),
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_class_results_list_with_one_class_but_without_results(
    event: EventType, class_info_1: ClassInfoType
) -> None:
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, [])],
            columns=set(),
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


def test_class_results_list_with_one_class_and_with_results(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
) -> None:
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns=set(),
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]


def test_class_results_list_with_two_classes_and_with_results(
    event: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
    entry_1: EntryType,
    entry_2: EntryType,
    entry_3: EntryType,
) -> None:
    results_list_1 = [RankedEntryType(entry=entry_1), RankedEntryType(entry_2)]
    results_list_2 = [RankedEntryType(entry=entry_3)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[
                (class_info_1.name, results_list_1),
                (class_info_2.name, results_list_2),
            ],
            columns=set(),
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 5

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "790"
    assert rows[2].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[2].findall(".//td")] == [
        None,
        "Merkel, Barbara",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert [th.text for th in rows[3].findall(".//th")] == [
        "Elite Men\xa0\xa0(1)",
    ]

    # row 5
    assert rows[4].attrib["data-id"] == "791"
    assert rows[4].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[4].findall(".//td")] == [
        None,
        "Derkel, Bernd",
        None,
        None,
        None,
        None,
        None,
    ]


def test_score(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
) -> None:
    class_info_1.params.otype = "score"
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


@pytest.mark.parametrize(
    "status, text, run_time",
    [
        (ResultStatus.ACTIVE, "Started", None),
        (ResultStatus.FINISHED, "Finished", "6:57"),
        (ResultStatus.MISSING_PUNCH, "MP", None),
        (ResultStatus.DID_NOT_START, "DNS", None),
        (ResultStatus.DID_NOT_FINISH, "DNF", None),
        (ResultStatus.OVER_TIME, "OTL", None),
        (ResultStatus.DISQUALIFIED, "DSQ", None),
    ],
)
def test_score_and_status_is_not_inactive_or_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    status: ResultStatus,
    text: Optional[str],
    run_time: Optional[str],
) -> None:
    class_info_1.params.otype = "score"
    entry_1.result.status = status
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        run_time,
        None,
        None,
        text,
    ]


def test_score_and_status_is_ok(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
) -> None:
    class_info_1.params.otype = "score"
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "score_controls": 12.4,
        "score_overtime": 2.1,
        "score": 45.1,
    }
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "6:57",
        "12.40",
        "2.10",
        "45.10",
    ]


def test_score_and_status_is_ok_but_no_values_defined(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.otype = "score"
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.result.extensions = {"score": 45.72}
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "6:57",
        None,
        None,
        "45.72",
    ]


def test_score_status_is_inactive_with_start_time(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.otype = "score"
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
        None,
        "Start at 12:38:59",
    ]


def test_score_and_handicap_defined_and_status_is_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.otype = "score"
    class_info_1.params.apply_handicap_rule = True
    entry_1.year = 1960
    entry_1.gender = "F"
    entry_1.result.extensions = {"factor": 0.4567}
    entry_1.result.status = ResultStatus.OK
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score", "factor"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        "1960",
        None,
        None,
        "0.4567",
        None,
        None,
        None,
        "OK",
    ]


def test_score_and_handicap_defined_but_status_is_not_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.otype = "score"
    class_info_1.params.apply_handicap_rule = True
    entry_1.year = 1960
    entry_1.gender = "F"
    entry_1.result.extensions = {"factor": 0.4567}
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"score", "factor"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "Sc. controls",
        "Sc. overtime",
        "Total score",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        "1960",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_class_results_list_no_score_all_columns(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    class_info_1.params.apply_handicap_rule = True
    entry_1.year = 1960
    entry_1.gender = "F"
    entry_1.result.extensions = {"factor": 0.4567}
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"factor", "penalties_controls", "penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "P. controls",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        "1960",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_no_score_and_handicap_defined_and_status_is_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.apply_handicap_rule = True
    entry_1.gender = "F"
    entry_1.result.extensions = {"factor": 0.4567}
    entry_1.result.status = ResultStatus.OK
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"factor"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "0.4567",
        None,
        "OK",
    ]


def test_no_score_and_handicap_defined_and_status_is_not_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.apply_handicap_rule = True
    entry_1.year = 1960
    entry_1.result.extensions = {"factor": 0.4567}
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"factor"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        "1960",
        None,
        None,
        None,
        None,
        None,
    ]

    def test_no_score_with_handicap_with_year_and_gender_defined(
        event: EventType,
        class_info_1: ClassInfoType,
        entry_1: EntryType,
    ) -> None:
        class_info_1.params.apply_handicap_rule = True
        entry_1.year = 1960
        entry_1.gender = "F"
        entry_1.result.extensions = {"factor": 0.4567}
        results_list = [RankedEntryType(entry=entry_1)]
        html = Html(
            text=render.entries_table(
                event=event,
                view="results",
                view_entries_list=[(class_info_1.name, results_list)],
                columns={"factor"},
            )
        )

        assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
        assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

        # headers
        headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
        assert [h.text for h in headers] == [
            "Rank",
            "Name",
            "Year",
            "Chip",
            "Club",
            "Handicap",
            "Run time",
            "Total time",
        ]

        # rows
        rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
        assert len(rows) == 2

        # row 1
        assert [th.text for th in rows[0].findall(".//th")] == [
            "Elite Women\xa0\xa0(1)",
        ]

        # row 2
        assert rows[1].attrib["data-id"] == "789"
        assert rows[1].attrib["data-assigned"] == "true"
        assert [td.text for td in rows[1].findall(".//td")] == [
            None,
            "Merkel, Angela",
            None,
            None,
            None,
            "0.4567",
            None,
            "OK",
        ]


@pytest.mark.parametrize(
    "status, text, run_time",
    [
        (ResultStatus.ACTIVE, "Started", None),
        (ResultStatus.FINISHED, "Finished", "6:57"),
        (ResultStatus.MISSING_PUNCH, "MP", None),
        (ResultStatus.DID_NOT_START, "DNS", None),
        (ResultStatus.DID_NOT_FINISH, "DNF", None),
        (ResultStatus.OVER_TIME, "OTL", None),
        (ResultStatus.DISQUALIFIED, "DSQ", None),
    ],
)
def test_no_score_and_status_is_not_inactive_or_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    status: ResultStatus,
    text: Optional[str],
    run_time: Optional[str],
) -> None:
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = status
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"penalties_controls", "penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "P. controls",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        run_time,
        None,
        None,
        text,
    ]


def test_no_score_and_status_is_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "running_time": 313,
        "penalties_controls": 112,
        "penalties_overtime": 212,
    }
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"penalties_controls", "penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "P. controls",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "5:13",
        "1:52",
        "3:32",
        "6:57",
    ]


def test_no_score_and_status_is_ok_but_no_values_defined(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"factor", "penalties_controls", "penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Handicap",
        "Run time",
        "P. controls",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "6:57",
    ]


def test_no_score_status_is_inactive_with_start_time(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"penalties_controls", "penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "P. controls",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
        None,
        "Start at 12:38:59",
    ]


def test_no_score_and_status_is_ok_and_only_penalties_controls(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.penalty_controls = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "running_time": 313,
        "penalties_controls": 112,
    }
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"penalties_controls"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "P. controls",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "5:13",
        "1:52",
        "6:57",
    ]


def test_no_score_and_status_is_ok_and_only_penalties_overtime(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
) -> None:
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "running_time": 313,
        "penalties_overtime": 212,
    }
    results_list = [RankedEntryType(entry=entry_1)]
    html = Html(
        text=render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(class_info_1.name, results_list)],
            columns={"penalties_overtime"},
        )
    )

    assert html.find(path=".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(path=".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(path=f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "P. overtime",
        "Total time",
    ]

    # rows
    rows = html.findall(path=f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 2

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Elite Women\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "789"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        "5:13",
        "3:32",
        "6:57",
    ]

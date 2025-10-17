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
from typing import List
from typing import Optional

import pytest
from lxml import etree

from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import ResultStatus
from ooresults.utils import render


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
        year=1957,
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


def test_class_results_list_is_empty(event: EventType):
    html = etree.HTML(render.si1_results(event=event, class_results=[]))

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == []


def test_class_results_list_with_one_class_but_without_results(
    event: EventType, class_info_1: ClassInfoType
):
    html = etree.HTML(
        render.si1_results(event=event, class_results=[(class_info_1, [])])
    )

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == []


def test_class_results_list_with_one_class_and_with_results(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # headers
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Elite Women"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == [
        "Rank",
        "Name",
        "Year",
        "Club",
        "Time",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 1

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        None,
        "Angela Merkel",
        "1957",
        None,
        None,
    ]


def test_rank_is_defined(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1, rank=3)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[1]")
    assert elem.text == "3"


def test_entry_is_not_competing(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.not_competing = True
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[1]")
    assert elem.text == "NC"


@pytest.mark.parametrize(
    "year, text",
    [
        (None, None),
        (1941, "1941"),
        (2012, "2012"),
    ],
)
def test_year(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    year: Optional[int],
    text: Optional[str],
):
    entry_1.year = year
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[3]")
    assert elem.text == text


@pytest.mark.parametrize(
    # Club names with more than 20 characters will be truncated
    "club_name, text",
    [
        (None, None),
        ("OL Bundestag", "OL Bundestag"),
        ("OL Bundestagfraktion", "OL Bundestagfraktion"),
        ("OL Bundestagfraktion ", "OL Bundestagfraktion ..."),
        ("OL Bundestagfraktion der Grünen", "OL Bundestagfraktion ..."),
    ],
)
def test_club(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    club_name: Optional[str],
    text: Optional[str],
):
    entry_1.club_id = 57
    entry_1.club_name = club_name
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[4]")
    assert elem.text == text


def test_status_is_inactive_with_start_time(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.result.status = ResultStatus.INACTIVE
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[5]")
    assert elem.text == "Start at 12:38:59"


def test_status_is_ok(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[5]")
    assert elem.text == "6:57"


@pytest.mark.parametrize(
    "status, text",
    [
        (ResultStatus.ACTIVE, "Started"),
        (ResultStatus.FINISHED, "Finished"),
        (ResultStatus.MISSING_PUNCH, "MP"),
        (ResultStatus.DID_NOT_START, "DNS"),
        (ResultStatus.DID_NOT_FINISH, "DNF"),
        (ResultStatus.OVER_TIME, "OTL"),
        (ResultStatus.DISQUALIFIED, "DSQ"),
    ],
)
def test_status_is_not_inactive_or_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    status: ResultStatus,
    text: Optional[str],
):
    entry_1.result.status = status
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[5]")
    assert elem.text == text


def test_class_results_list_with_two_classes_and_with_results(
    event: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
    entry_1: EntryType,
    entry_2: EntryType,
    entry_3: EntryType,
):
    class_results = [
        (class_info_1, [RankedEntryType(entry=entry_1), RankedEntryType(entry_2)]),
        (class_info_2, [RankedEntryType(entry=entry_3)]),
    ]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == ["thead", "tbody", "thead", "tbody"]

    # headers
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Elite Women"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == [
        "Rank",
        "Name",
        "Year",
        "Club",
        "Time",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 2

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        None,
        "Angela Merkel",
        "1957",
        None,
        None,
    ]

    # row 2
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Barbara Merkel",
        None,
        None,
        None,
    ]

    # headers
    headers = table.findall("./thead[2]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Elite Men"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == [
        "Rank",
        "Name",
        "Year",
        "Club",
        "Time",
    ]

    # rows
    rows = table.findall("./tbody[2]/tr")
    assert len(rows) == 1

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        None,
        "Bernd Derkel",
        None,
        None,
        None,
    ]


def check_header(html: etree.Element, values: List[str]) -> None:
    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # headers
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Elite Women"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == values


def check_row(html: etree.Element, values: List[Optional[str]]) -> None:
    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # headers
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 2

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 1

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == values


def test_score(event: EventType, class_info_1: ClassInfoType, entry_1: EntryType):
    class_info_1.params.otype = "score"
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Score",
            "Penalty",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            None,
            None,
        ],
    )


@pytest.mark.parametrize(
    "status, text",
    [
        (ResultStatus.ACTIVE, "Started"),
        (ResultStatus.FINISHED, "Finished"),
        (ResultStatus.MISSING_PUNCH, "MP"),
        (ResultStatus.DID_NOT_START, "DNS"),
        (ResultStatus.DID_NOT_FINISH, "DNF"),
        (ResultStatus.OVER_TIME, "OTL"),
        (ResultStatus.DISQUALIFIED, "DSQ"),
    ],
)
def test_score_and_status_is_not_inactive_or_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    status: ResultStatus,
    text: Optional[str],
):
    class_info_1.params.otype = "score"
    entry_1.result.status = status
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Score",
            "Penalty",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            None,
            text,
        ],
    )


def test_score_and_status_is_ok(
    event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    class_info_1.params.otype = "score"
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "score_controls": 12.4,
        "score_overtime": 2.1,
        "score": 45.1,
    }
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Score",
            "Penalty",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            "6:57",
            "12.40",
            "2.10",
            "45.10",
        ],
    )


def test_score_and_status_is_ok_but_no_values_defined(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.result.extensions = {"score": 45.72}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Score",
            "Penalty",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            "6:57",
            None,
            None,
            "45.72",
        ],
    )


def test_score_status_is_inactive_with_start_time(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Score",
            "Penalty",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            None,
            "Start at 12:38:59",
        ],
    )


def test_class_results_list_no_score_all_columns(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    class_info_1.params.apply_handicap_rule = True
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            None,
        ],
    )


@pytest.mark.parametrize(
    "status, text",
    [
        (ResultStatus.ACTIVE, "Started"),
        (ResultStatus.FINISHED, "Finished"),
        (ResultStatus.MISSING_PUNCH, "MP"),
        (ResultStatus.DID_NOT_START, "DNS"),
        (ResultStatus.DID_NOT_FINISH, "DNF"),
        (ResultStatus.OVER_TIME, "OTL"),
        (ResultStatus.DISQUALIFIED, "DSQ"),
    ],
)
def test_no_score_and_status_is_not_inactive_or_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
    status: ResultStatus,
    text: Optional[str],
):
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = status
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            text,
        ],
    )


def test_no_score_and_status_is_ok(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
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
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            "5:13",
            "5:24",
            "6:57",
        ],
    )


def test_no_score_and_status_is_ok_but_no_values_defined(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.result.extensions = {"score": 45.72}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            "6:57",
        ],
    )


def test_no_score_status_is_inactive_with_start_time(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.penalty_controls = 30
    class_info_1.params.penalty_overtime = 30
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            None,
            None,
            "Start at 12:38:59",
        ],
    )


def test_no_score_and_status_is_ok_and_only_penalties_controls(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.penalty_controls = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "running_time": 313,
        "penalties_controls": 112,
        "penalties_overtime": 212,
    }
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            "5:13",
            "1:52",
            "6:57",
        ],
    )


def test_no_score_and_status_is_ok_and_only_penalties_overtime(
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.penalty_overtime = 30
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    entry_1.result.extensions = {
        "running_time": 313,
        "penalties_controls": 112,
        "penalties_overtime": 212,
    }
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(render.si1_results(event=event, class_results=class_results))

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Year",
            "Club",
            "Run time",
            "Penalty",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            "1957",
            None,
            "5:13",
            "3:32",
            "6:57",
        ],
    )

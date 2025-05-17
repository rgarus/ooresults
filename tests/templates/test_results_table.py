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
from typing import Optional

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import ResultStatus
from ooresults.utils.globals import t_globals


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


def test_class_results_list_is_empty(render, event: EventType):
    html = etree.HTML(
        str(render.results_table(event=event, class_results=[], columns=set()))
    )

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == []


def test_class_results_list_with_one_class_but_without_results(
    render, event: EventType, class_info_1: ClassInfoType
):
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=[(class_info_1, [])], columns=set()
            )
        )
    )

    assert html.find(".//div[@id='res.event']//tr[1]//td").text == "Test-Lauf 1"
    assert html.find(".//div[@id='res.event']//tr[2]//td").text == "2023-12-29"

    table = html.find(".//div[@id='res.result']/table")
    assert [child.tag for child in table] == []


def test_class_results_list_with_one_class_and_with_results(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

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
        None,
        None,
    ]


def test_rank_is_defined(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1, rank=3)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[1]")
    assert elem.text == "3"


def test_entry_is_not_competing(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.not_competing = True
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[1]")
    assert elem.text == "NC"


def test_club_is_defined(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.club_id = 57
    entry_1.club_name = "OL Bundestag"
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[3]")
    assert elem.text == "OL Bundestag"


def test_status_is_inactive_with_start_time(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.result.status = ResultStatus.INACTIVE
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[4]")
    assert elem.text == "Start at 12:38:59"


def test_status_is_ok(
    render, event: EventType, class_info_1: ClassInfoType, entry_1: EntryType
):
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[4]")
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
    render,
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
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

    elem = html.find(".//div[@id='res.result']/table/tbody[1]/tr[1]/td[4]")
    assert elem.text == text


def test_class_results_list_with_two_classes_and_with_results(
    render,
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
    html = etree.HTML(
        str(
            render.results_table(
                event=event, class_results=class_results, columns=set()
            )
        )
    )

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
        None,
        None,
    ]

    # row 2
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Barbara Merkel",
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


def test_score(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
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
    render,
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
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            None,
            None,
            None,
            text,
        ],
    )


def test_score_and_status_is_ok(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
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
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "6:57",
            "12.40",
            "2.10",
            "45.10",
        ],
    )


def test_score_and_status_is_ok_but_no_values_defined(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.result.extensions = {"score": 45.72}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "6:57",
            None,
            None,
            "45.72",
        ],
    )


def test_score_status_is_inactive_with_start_time(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            None,
            None,
            None,
            "Start at 12:38:59",
        ],
    )


def test_score_and_handicap_without_factor_defined(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score", "factor"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Handicap",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "1.0000",
            None,
            None,
            None,
            None,
        ],
    )


def test_score_and_handicap_with_factor_defined(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_info_1.params.otype = "score"
    entry_1.result.extensions = {"factor": 0.4567}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"score_controls", "score_overtime", "score", "factor"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Handicap",
            "Run time",
            "Score controls",
            "Score overtime",
            "Total score",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "0.4567",
            None,
            None,
            None,
            None,
        ],
    )


def test_class_results_list_no_score_all_columns(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls", "penalties_overtime", "factor"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Handicap",
            "Run time",
            "Penalty controls",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "1.0000",
            None,
            None,
            None,
            None,
        ],
    )


def test_no_score_with_handicap_and_factor_defined(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    entry_1.result.extensions = {"factor": 0.4567}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"factor"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Handicap",
            "Run time",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "0.4567",
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
    render,
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
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls", "penalties_overtime"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty controls",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            None,
            None,
            None,
            text,
        ],
    )


def test_no_score_and_status_is_ok(
    render,
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
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls", "penalties_overtime"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty controls",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "5:13",
            "1:52",
            "3:32",
            "6:57",
        ],
    )


def test_no_score_and_status_is_ok_but_no_values_defined(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    entry_1.result.status = ResultStatus.OK
    entry_1.result.time = 417
    entry_1.result.extensions = {"score": 45.72}
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls", "penalties_overtime"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty controls",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            None,
            None,
            None,
            "6:57",
        ],
    )


def test_no_score_status_is_inactive_with_start_time(
    render,
    event: EventType,
    class_info_1: ClassInfoType,
    entry_1: EntryType,
):
    entry_1.result.time = 417
    entry_1.start.start_time = S1
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls", "penalties_overtime"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty controls",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            None,
            None,
            None,
            "Start at 12:38:59",
        ],
    )


def test_no_score_and_status_is_ok_and_only_penalties_controls(
    render,
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
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_controls"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty controls",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "5:13",
            "1:52",
            "6:57",
        ],
    )


def test_no_score_and_status_is_ok_and_only_penalties_overtime(
    render,
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
    class_results = [(class_info_1, [RankedEntryType(entry=entry_1)])]
    html = etree.HTML(
        str(
            render.results_table(
                event=event,
                class_results=class_results,
                columns={"penalties_overtime"},
            )
        )
    )

    check_header(
        html=html,
        values=[
            "Rank",
            "Name",
            "Club",
            "Run time",
            "Penalty overtime",
            "Total time",
        ],
    )

    check_row(
        html=html,
        values=[
            None,
            "Angela Merkel",
            None,
            "5:13",
            "3:32",
            "6:57",
        ],
    )

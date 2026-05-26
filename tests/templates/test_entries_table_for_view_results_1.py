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
from lxml import etree

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


TABLE_ID = "entr.table"


def test_entries_list_is_empty(event: EventType):
    html = etree.HTML(
        render.entries_table(
            event=event, view="results", view_entries_list=[], columns=set()
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


@pytest.fixture()
def ranked_entry_1(event: EventType) -> RankedEntryType:
    return RankedEntryType(
        entry=EntryType(
            id=123,
            event_id=event.id,
            competitor_id=None,
            first_name=None,
            last_name=None,
        )
    )


@pytest.fixture()
def ranked_entry_2(event: EventType) -> RankedEntryType:
    return RankedEntryType(
        entry=EntryType(
            id=456,
            event_id=event.id,
            competitor_id=122,
            first_name="Barbara",
            last_name="Merkel",
        )
    )


@pytest.fixture()
def ranked_entry_3(event: EventType) -> RankedEntryType:
    return RankedEntryType(
        entry=EntryType(
            id=789,
            event_id=event.id,
            competitor_id=123,
            first_name="Angela",
            last_name="Merkel",
        )
    )


@pytest.fixture()
def ranked_entries(
    ranked_entry_1: RankedEntryType,
    ranked_entry_2: RankedEntryType,
    ranked_entry_3: RankedEntryType,
) -> list[RankedEntryType]:
    return [ranked_entry_1, ranked_entry_2, ranked_entry_3]


def test_entry_list_with_one_group(
    event: EventType, ranked_entries: list[RankedEntryType]
):
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Group XY\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "123"
    assert rows[1].attrib["data-assigned"] == "false"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "456"
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
    assert rows[3].attrib["data-id"] == "789"
    assert rows[3].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]


def test_entry_list_with_unassigned_group(
    event: EventType, ranked_entries: list[RankedEntryType]
):
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[(None, ranked_entries)],
            columns=set(),
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Unassigned results\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "123"
    assert rows[1].attrib["data-assigned"] == "false"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "456"
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
    assert rows[3].attrib["data-id"] == "789"
    assert rows[3].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]


def test_entry_list_with_two_groups(
    event: EventType,
    ranked_entry_1: RankedEntryType,
    ranked_entry_2: RankedEntryType,
    ranked_entry_3: RankedEntryType,
):
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[
                ("Up and down", [ranked_entry_2, ranked_entry_3]),
                ("Dies und das", [ranked_entry_1]),
            ],
            columns=set(),
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 5

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Up and down\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "456"
    assert rows[1].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Merkel, Barbara",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "789"
    assert rows[2].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[2].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert [th.text for th in rows[3].findall(".//th")] == [
        "Dies und das\xa0\xa0(1)",
    ]

    # row 5
    assert rows[4].attrib["data-id"] == "123"
    assert rows[4].attrib["data-assigned"] == "false"
    assert [td.text for td in rows[4].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_entry_list_with_three_groups(
    event: EventType,
    ranked_entry_1: RankedEntryType,
    ranked_entry_2: RankedEntryType,
    ranked_entry_3: RankedEntryType,
):
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[
                ("Group 1", [ranked_entry_1]),
                ("Group 2", [ranked_entry_2]),
                ("Group 3", [ranked_entry_3]),
            ],
            columns=set(),
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 6

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Group 1\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "123"
    assert rows[1].attrib["data-assigned"] == "false"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert [th.text for th in rows[2].findall(".//th")] == [
        "Group 2\xa0\xa0(1)",
    ]

    # row 4
    assert rows[3].attrib["data-id"] == "456"
    assert rows[3].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Merkel, Barbara",
        None,
        None,
        None,
        None,
        None,
    ]

    # row 5
    assert [th.text for th in rows[4].findall(".//th")] == [
        "Group 3\xa0\xa0(1)",
    ]

    # row 6
    assert rows[5].attrib["data-id"] == "789"
    assert rows[5].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[5].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]


def test_not_competing_is_true(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].entry.not_competing = True
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[1]")
    assert elem.text == "NC"


def test_rank_is_defined(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].rank = 14
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[1]")
    assert elem.text == "14"


def test_last_name_is_defined(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].entry.last_name = "Derkel"
    ranked_entries[0].entry.first_name = "Barbara"

    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[2]")
    assert elem.text == "Derkel, Barbara"


def test_year_is_defined(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].entry.year = 1957
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "1957"


def test_chip_is_defined(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].entry.chip = "1234567"
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "1234567"


@pytest.mark.parametrize(
    "name, displayed_name",
    [
        ("1234567890123456789", "1234567890123456789"),
        ("12345678901234567890", "123456789012345 ..."),
        ("123456789012345678901", "123456789012345 ..."),
    ],
)
def test_club_is_shortened_if_view_is_results(
    event: EventType,
    ranked_entries: list[RankedEntryType],
    name: str,
    displayed_name: str,
):
    ranked_entries[0].entry.club_id = 3
    ranked_entries[0].entry.club_name = name
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("None", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == displayed_name


def test_status_is_inactive_with_start_time(
    event: EventType, ranked_entries: list[RankedEntryType]
):

    ranked_entries[0].entry.result.status = ResultStatus.INACTIVE
    ranked_entries[0].entry.result.time = 417
    ranked_entries[0].entry.start.start_time = S1
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("None", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text is None
    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "Start at 12:38:59"


def test_total_time_is_defined(event: EventType, ranked_entries: list[RankedEntryType]):
    ranked_entries[0].entry.result.status = ResultStatus.OK
    ranked_entries[0].entry.result.time = 8
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text is None
    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "0:08"


@pytest.mark.parametrize(
    "status, text",
    [
        (ResultStatus.INACTIVE, None),
        (ResultStatus.ACTIVE, "Started"),
        (ResultStatus.FINISHED, "Finished"),
        (ResultStatus.OK, "OK"),
        (ResultStatus.MISSING_PUNCH, "MP"),
        (ResultStatus.DID_NOT_START, "DNS"),
        (ResultStatus.DID_NOT_FINISH, "DNF"),
        (ResultStatus.OVER_TIME, "OTL"),
        (ResultStatus.DISQUALIFIED, "DSQ"),
    ],
)
def test_status(
    event: EventType,
    ranked_entries: list[RankedEntryType],
    status: ResultStatus,
    text: Optional[str],
):
    ranked_entries[0].entry.result.status = status
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == text


def test_entry_list_with_fields(
    event: EventType, ranked_entries: list[RankedEntryType]
):
    event.fields = ["Start number", "Region"]
    ranked_entries[0].entry.fields = {0: "121", 1: "Bayern"}
    html = etree.HTML(
        render.entries_table(
            event=event,
            view="results",
            view_entries_list=[("Group XY", ranked_entries)],
            columns=set(),
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
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
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Group XY\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["data-id"] == "123"
    assert rows[1].attrib["data-assigned"] == "false"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["data-id"] == "456"
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
    assert rows[3].attrib["data-id"] == "789"
    assert rows[3].attrib["data-assigned"] == "true"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Merkel, Angela",
        None,
        None,
        None,
        None,
        None,
    ]

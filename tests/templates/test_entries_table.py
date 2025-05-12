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
from ooresults.otypes.entry_type import EntryType
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


TABLE_ID = "entr.table"


def test_entries_list_is_empty(render, event: EventType):
    html = etree.HTML(
        str(render.entries_table(event=event, view="Entries", view_entries_list=[]))
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr/")
    assert len(rows) == 0


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)


@pytest.fixture()
def entry_1(event: EventType) -> EntryType:
    return EntryType(
        id=123,
        event_id=event.id,
        competitor_id=None,
        first_name=None,
        last_name=None,
    )


@pytest.fixture()
def entry_2(event: EventType) -> EntryType:
    return EntryType(
        id=456,
        event_id=event.id,
        competitor_id=122,
        first_name="Barbara",
        last_name="Merkel",
    )


@pytest.fixture()
def entry_3(event: EventType) -> EntryType:
    return EntryType(
        id=789,
        event_id=event.id,
        competitor_id=123,
        first_name="Angela",
        last_name="Merkel",
    )


@pytest.fixture()
def entries(
    entry_1: EntryType, entry_2: EntryType, entry_3: EntryType
) -> List[EntryType]:
    return [entry_1, entry_2, entry_3]


def test_entry_list_with_one_group(render, event: EventType, entries: List[EntryType]):
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Entries\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "123"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "456"
    assert [td.text for td in rows[2].findall(".//td")] == [
        None,
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["id"] == "789"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Angela",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_entry_list_with_two_groups(
    render, event: EventType, entry_1: EntryType, entry_2: EventType, entry_3: EntryType
):
    html = etree.HTML(
        str(
            render.entries_table(
                event=event,
                view="entries",
                view_entries_list=[
                    ("Up and down", [entry_2, entry_3]),
                    ("Dies und das", [entry_1]),
                ],
            )
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 5

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Up and down\xa0\xa0(2)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "456"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "789"
    assert [td.text for td in rows[2].findall(".//td")] == [
        None,
        "Angela",
        "Merkel",
        None,
        None,
        None,
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
    assert rows[4].attrib["id"] == "123"
    assert [td.text for td in rows[4].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_entry_list_with_three_groups(
    render, event: EventType, entry_1: EntryType, entry_2: EventType, entry_3: EntryType
):
    html = etree.HTML(
        str(
            render.entries_table(
                event=event,
                view="entries",
                view_entries_list=[
                    ("Group 1", [entry_1]),
                    ("Group 2", [entry_2]),
                    ("Group 3", [entry_3]),
                ],
            )
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 6

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Group 1\xa0\xa0(1)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "123"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
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
    assert rows[3].attrib["id"] == "456"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Barbara",
        "Merkel",
        None,
        None,
        None,
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
    assert rows[5].attrib["id"] == "789"
    assert [td.text for td in rows[5].findall(".//td")] == [
        None,
        "Angela",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]


def test_not_competing_is_true(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].not_competing = True
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[1]")
    assert elem.text == "X"


def test_first_name_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].first_name = "Sabine"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[2]")
    assert elem.text == "Sabine"


def test_last_name_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].last_name = "Derkel"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[3]")
    assert elem.text == "Derkel"


def test_gender_is_unknown(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].gender = ""
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text is None


def test_gender_is_female(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].gender = "F"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "F"


def test_gender_is_male(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].gender = "M"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[4]")
    assert elem.text == "M"


def test_year_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].year = 1957
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[5]")
    assert elem.text == "1957"


def test_chip_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].chip = "1234567"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[6]")
    assert elem.text == "1234567"


def test_club_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].club_id = 3
    entries[0].club_name = "OC Bundestag"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[7]")
    assert elem.text == "OC Bundestag"


def test_class_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].class_id = 7
    entries[0].class_name = "Elite Men"
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[8]")
    assert elem.text == "Elite Men"


def test_start_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].start.start_time = S1
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[9]")
    assert elem.text == "12:38:59"


def test_time_is_defined(
    render,
    event: EventType,
    entries: List[EntryType],
):
    entries[0].result.time = 8
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[10]")
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
    render,
    event: EventType,
    entries: List[EntryType],
    status: ResultStatus,
    text: Optional[str],
):
    entries[0].result.status = status
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="Entries", view_entries_list=[("Entries", entries)]
            )
        )
    )

    elem = html.find(f".//table[@id='{TABLE_ID}']/tbody/tr[2]/td[11]")
    assert elem.text == text


def test_entry_list_with_fields(render, event: EventType, entries: List[EntryType]):
    event.fields = ["Start number", "Region"]
    entries[0].fields = {0: "121", 1: "Bayern"}
    html = etree.HTML(
        str(
            render.entries_table(
                event=event, view="entries", view_entries_list=[(None, entries)]
            )
        )
    )

    assert html.find(".//td[@id='entr.event_name']").text == "Test-Lauf 1"
    assert html.find(".//td[@id='entr.event_date']").text == "2023-12-29"

    # headers
    headers = html.findall(f".//table[@id='{TABLE_ID}']/thead/tr/th")
    assert [h.text for h in headers] == [
        "\xa0\xa0NC\xa0\xa0",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start number",
        "Region",
        "Start",
        "Time",
        "Status",
    ]

    # rows
    rows = html.findall(f".//table[@id='{TABLE_ID}']/tbody/tr")
    assert len(rows) == 4

    # row 1
    assert [th.text for th in rows[0].findall(".//th")] == [
        "Entries\xa0\xa0(3)",
    ]

    # row 2
    assert rows[1].attrib["id"] == "123"
    assert [td.text for td in rows[1].findall(".//td")] == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "121",
        "Bayern",
        None,
        None,
        None,
    ]

    # row 3
    assert rows[2].attrib["id"] == "456"
    assert [td.text for td in rows[2].findall(".//td")] == [
        None,
        "Barbara",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

    # row 4
    assert rows[3].attrib["id"] == "789"
    assert [td.text for td in rows[3].findall(".//td")] == [
        None,
        "Angela",
        "Merkel",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]

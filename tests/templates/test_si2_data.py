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
from typing import Optional

import pytest
from lxml import etree

from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import ResultStatus
from ooresults.utils import render
from ooresults.websocket_server.streaming_status import Status


@pytest.fixture()
def event() -> EventType:
    return EventType(
        id=3,
        name="1. O-Cup 2023",
        date=datetime.date(
            year=2023,
            month=1,
            day=15,
        ),
        key="local",
        publish=False,
        series="Lauf 1",
        fields=[],
    )


#
# status: Optional[str] = None
# stream_status: Optional[streaming_status.Status] = None
# event: Optional[EventType] = None
# messages: List[Dict] = []
#

#
# message:
#   "entryTime": datetime.datetime
#   "eventId": int
#   "controlCard": str
#   "firstName": str
#   "lastName": str
#   "club": str
#   "class": str
#   "status": result.status
#   "time": int
#   "error": str
#   "missingControls": List[str]
#


def test_messages_list_is_empty_with_stream_status_is_none(event: EventType):
    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=[]
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]
    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 0

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]
    assert [td.text for td in table.findall("./tr[1]/td")] == ["Connected"]


def test_messages_list_is_empty_with_stream_status_is_not_none(event: EventType):
    html = etree.HTML(
        render.si2_data(
            status="readerConnected",
            stream_status=Status.NOT_CONNECTED,
            event=event,
            messages=[],
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]
    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 0

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr", "tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]
    assert [td.text for td in table.findall("./tr[1]/td")] == ["Connected"]
    assert [th.text for th in table.findall("./tr[2]/th")] == ["Stream status:"]
    assert [td.text for td in table.findall("./tr[2]/td")] == ["Not connected"]


def test_messages_for_same_event_id_are_displayed(event: EventType):
    messages = [
        {
            "entryTime": "10:26:03",
            "eventId": event.id,
            "controlCard": "7379879",
            "firstName": "Annalena",
            "lastName": "Baerbock",
            "club": "OC Grün",
            "class": "Bahn A - Frauen",
            "status": ResultStatus.OK,
            "time": 879,
            "error": None,
            "missingControls": [],
        },
        {
            "entryTime": "10:28:03",
            "eventId": event.id,
            "controlCard": "7509749",
            "firstName": "Robert",
            "lastName": "Habeck",
            "club": "OC Grün",
            "class": "Bahn A - Männer",
            "status": ResultStatus.MISSING_PUNCH,
            "time": 844,
            "error": None,
            "missingControls": ["122"],
        },
        {
            "entryTime": "10:28:20",
            "eventId": event.id,
            "controlCard": "7223344",
            "firstName": None,
            "lastName": None,
            "club": None,
            "class": None,
            "status": ResultStatus.FINISHED,
            "time": None,
            "error": "Control card unknown",
        },
        {
            "entryTime": "10:35:20",
            "eventId": event.id,
            "controlCard": "7076815",
            "firstName": "Marco",
            "lastName": "Buschmann",
            "club": "OC Gelb",
            "class": "Bahn A - Männer",
            "status": ResultStatus.OK,
            "time": 1050,
            "error": None,
            "missingControls": [],
        },
    ]

    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=messages
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 4
    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        "10:26:03",
        "7379879",
        "OK",
        "14:39 min",
        "Baerbock, Annalena",
        "Bahn A - Frauen",
        None,
    ]
    # row 2
    assert [td.text for td in rows[1].findall(".//td")] == [
        "10:28:03",
        "7509749",
        "MP",
        "14:04 min",
        "Habeck, Robert",
        "Bahn A - Männer",
        "122",
    ]
    # row 3
    assert [td.text for td in rows[2].findall(".//td")] == [
        "10:28:20",
        "7223344",
        "Finished",
        None,
        "Control card unknown",
    ]
    # row 4
    assert [td.text for td in rows[3].findall(".//td")] == [
        "10:35:20",
        "7076815",
        "OK",
        "17:30 min",
        "Buschmann, Marco",
        "Bahn A - Männer",
        None,
    ]

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]


def test_messages_for_another_event_id_are_not_displayed(event: EventType):
    messages = [
        {
            "entryTime": "10:26:03",
            "eventId": event.id + 1,
            "controlCard": "7379879",
            "firstName": "Annalena",
            "lastName": "Baerbock",
            "club": "OC Grün",
            "class": "Bahn A - Frauen",
            "status": ResultStatus.OK,
            "time": 879,
            "error": None,
            "missingControls": [],
        },
    ]

    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=messages
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 0

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]


@pytest.mark.parametrize(
    "status, text, color",
    [
        (None, "Offline", "red"),
        ("readerOffline", "Offline", "red"),
        ("readerDisconnected", "Disconnected", "red"),
        ("readerConnected", "Connected", "green"),
        ("cardInserted", "Reading card", "green"),
        ("cardRemoved", "Connected", "green"),
        ("cardRead", "Connected", "green"),
    ],
)
def test_cardreader_status(
    event: EventType, status: Optional[str], text: str, color: str
):
    html = etree.HTML(
        render.si2_data(status=status, stream_status=None, event=event, messages=[])
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]
    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 0

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert table[0].attrib["style"] == f"color:{color};"
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]
    assert [td.text for td in table.findall("./tr[1]/td")] == [text]


@pytest.mark.parametrize(
    "status, text, color",
    [
        (Status.NOT_CONNECTED, "Not connected", "red"),
        (Status.INTERNAL_ERROR, "Internal error", "red"),
        (Status.PROTOCOL_ERROR, "Protocol error", "red"),
        (Status.EVENT_NOT_FOUND, "Event not found", "red"),
        (Status.ERROR, "Error", "red"),
        (Status.OK, "Ok", "green"),
    ],
)
def test_stream_status(event: EventType, status: Status, text: str, color: str):
    html = etree.HTML(
        render.si2_data(
            status="readerOffline", stream_status=status, event=event, messages=[]
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]
    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 0

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr", "tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]
    assert [td.text for td in table.findall("./tr[1]/td")] == ["Offline"]
    assert table[1].attrib["style"] == f"color:{color};"
    assert [th.text for th in table.findall("./tr[2]/th")] == ["Stream status:"]
    assert [td.text for td in table.findall("./tr[2]/td")] == [text]


@pytest.mark.parametrize(
    "missing_controls, text",
    [
        (["START", "121", "FINISH"], "Finish time"),
        (["START", "121"], "Start time"),
        (["121"], "121"),
        (["121", "124"], "121, 124"),
        (["121", "124", "122"], "121, 124, 122"),
        (["121", "124", "122", "123"], "4 controls"),
        (["121", "124", "122", "123", "124", "131"], "6 controls"),
    ],
)
def test_missing_controls_if_status_is_not_ok(
    event: EventType, missing_controls: list[str], text: str
):
    messages = [
        {
            "entryTime": "10:28:03",
            "eventId": event.id,
            "controlCard": "7509749",
            "firstName": "Robert",
            "lastName": "Habeck",
            "club": "OC Grün",
            "class": "Bahn A - Männer",
            "status": ResultStatus.MISSING_PUNCH,
            "time": 844,
            "error": None,
            "missingControls": missing_controls,
        },
    ]

    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=messages
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 1
    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        "10:28:03",
        "7509749",
        "MP",
        "14:04 min",
        "Habeck, Robert",
        "Bahn A - Männer",
        text,
    ]

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]


@pytest.mark.parametrize(
    "missing_controls, text",
    [
        (["121"], "1 control"),
        (["121", "124", "122", "123"], "4 controls"),
    ],
)
def test_missing_controls_if_status_is_ok(
    event: EventType, missing_controls: list[str], text: str
):
    messages = [
        {
            "entryTime": "10:28:03",
            "eventId": event.id,
            "controlCard": "7509749",
            "firstName": "Robert",
            "lastName": "Habeck",
            "club": "OC Grün",
            "class": "Bahn A - Männer",
            "status": ResultStatus.OK,
            "time": 844,
            "error": None,
            "missingControls": missing_controls,
        },
    ]

    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=messages
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1
    assert [td.text for td in headers[0].findall(".//th")] == [
        "Read",
        "Control card",
        "Status",
        "Time",
        "Name",
        "Class",
        "Missing controls",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 1
    # row 1
    assert rows[0].attrib["style"] == "background-color: #70ff70"
    assert [td.text for td in rows[0].findall(".//td")] == [
        "10:28:03",
        "7509749",
        "OK",
        "14:04 min",
        "Habeck, Robert",
        "Bahn A - Männer",
        text,
    ]

    # status
    table = html.find(".//div/table[@id='si2.status']")
    assert [child.tag for child in table] == ["tr"]
    assert [th.text for th in table.findall("./tr[1]/th")] == ["Card reader status:"]


@pytest.mark.parametrize(
    "result_status, color",
    [
        (ResultStatus.INACTIVE, "#ffff00"),
        (ResultStatus.ACTIVE, "#ffff00"),
        (ResultStatus.FINISHED, "#ffff00"),
        (ResultStatus.OK, "#70ff70"),
        (ResultStatus.MISSING_PUNCH, "#ff7070"),
        (ResultStatus.DID_NOT_START, "#ffff00"),
        (ResultStatus.DID_NOT_FINISH, "#ff7070"),
        (ResultStatus.OVER_TIME, "#ff7070"),
        (ResultStatus.DISQUALIFIED, "#ffff00"),
    ],
)
def test_messages_background_color_depends_on_status(
    event: EventType, result_status: ResultStatus, color: str
):
    messages = [
        {
            "entryTime": "10:28:03",
            "eventId": event.id,
            "controlCard": "7509749",
            "firstName": "Robert",
            "lastName": "Habeck",
            "club": "OC Grün",
            "class": "Bahn A - Männer",
            "status": result_status,
            "time": 844,
            "error": None,
            "missingControls": [],
        },
    ]

    html = etree.HTML(
        render.si2_data(
            status="readerConnected", stream_status=None, event=event, messages=messages
        )
    )

    assert html.find(".//div[@id='cls.event']//tr[1]//td").text == "1. O-Cup 2023"
    assert html.find(".//div[@id='cls.event']//tr[2]//td").text == "2023-01-15"

    # messages
    table = html.find(".//div/table[@id='si2.messages']")
    assert [child.tag for child in table] == ["thead", "tbody"]

    # header
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 1

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 1
    # row 1
    assert rows[0].attrib["style"] == f"background-color: {color}"

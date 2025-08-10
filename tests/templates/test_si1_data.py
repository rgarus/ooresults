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


from typing import Optional

import pytest
from lxml import etree

from ooresults.otypes.result_type import ResultStatus
from ooresults.utils import render


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


def test_status_is_ok():
    message = {
        "entryTime": "10:26:03",
        "eventId": 1,
        "controlCard": "7379879",
        "firstName": "Annalena",
        "lastName": "Baerbock",
        "club": "OC Grün",
        "class": "Bahn A - Frauen",
        "status": ResultStatus.OK,
        "time": 879,
        "error": None,
        "missingControls": [],
    }

    html = etree.HTML(render.si1_data(message=message))
    div = html.find(".//div[@id='si1.div']")
    assert div.attrib["class"] == "bgg"

    t = html.find(".//div[@id='si1.div']/div[1]/p").text
    assert t == "Baerbock, Annalena"
    t = html.find(".//div[@id='si1.div']/div[2]/p").text
    assert t == "7379879, Bahn A - Frauen"
    t = html.find(".//div[@id='si1.div']/div[3]/p").text
    assert t == "OK, 14:39 min"


def test_status_is_missing_punch():
    message = {
        "entryTime": "10:28:03",
        "eventId": 1,
        "controlCard": "7509749",
        "firstName": "Robert",
        "lastName": "Habeck",
        "club": "OC Grün",
        "class": "Bahn A - Männer",
        "status": ResultStatus.MISSING_PUNCH,
        "time": 844,
        "error": None,
        "missingControls": ["122"],
    }

    html = etree.HTML(render.si1_data(message=message))

    div = html.find(".//div[@id='si1.div']")
    assert div.attrib["class"] == "bgr"

    t = html.find(".//div[@id='si1.div']/div[1]/p").text
    assert t == "Habeck, Robert"
    t = html.find(".//div[@id='si1.div']/div[2]/p").text
    assert t == "7509749, Bahn A - Männer"
    t = html.find(".//div[@id='si1.div']/div[3]/p").text
    assert t == "MP"


@pytest.mark.parametrize(
    "result_status",
    [
        ResultStatus.INACTIVE,
        ResultStatus.ACTIVE,
        ResultStatus.FINISHED,
        ResultStatus.OK,
        ResultStatus.MISSING_PUNCH,
        ResultStatus.DID_NOT_START,
        ResultStatus.DID_NOT_FINISH,
        ResultStatus.OVER_TIME,
        ResultStatus.DISQUALIFIED,
    ],
)
def test_background_color_depends_on_result_status(result_status: ResultStatus):
    message = {
        "entryTime": "10:28:03",
        "eventId": 1,
        "controlCard": "7509749",
        "firstName": "Robert",
        "lastName": "Habeck",
        "club": "OC Grün",
        "class": "Bahn A - Männer",
        "status": result_status,
        "time": 844,
        "error": None,
        "missingControls": [],
    }

    html = etree.HTML(render.si1_data(message=message))

    div = html.find(".//div[@id='si1.div']")
    if result_status == ResultStatus.OK:
        assert div.attrib["class"] == "bgg"
    else:
        assert div.attrib["class"] == "bgr"


@pytest.mark.parametrize(
    "result_status, text",
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
def test_background_status_and_time_depends_on_result_status(
    result_status: ResultStatus, text: Optional[str]
):
    message = {
        "entryTime": "10:28:03",
        "eventId": 1,
        "controlCard": "7509749",
        "firstName": "Robert",
        "lastName": "Habeck",
        "club": "OC Grün",
        "class": "Bahn A - Männer",
        "status": result_status,
        "time": 844,
        "error": None,
        "missingControls": [],
    }

    html = etree.HTML(render.si1_data(message=message))

    t = html.find(".//div[@id='si1.div']/div[3]/p").text
    if result_status == ResultStatus.OK:
        assert t == "OK, 14:04 min"
    else:
        assert t == text

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


def test_error_is_not_empty():
    message = {
        "entryTime": "10:28:20",
        "eventId": 1,
        "controlCard": "7223344",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "Control card unknown",
    }

    html = etree.HTML(render.si1_error(message=message))
    div = html.find(".//div[@id='si1.div']")
    assert div.attrib["class"] == "bgy"

    t = html.find(".//div[@id='si1.div']/div[1]/p").text
    assert t == "7223344"
    t = html.find(".//div[@id='si1.div']/div[2]/p").text
    assert t == "Control card unknown"
    t = html.find(".//div[@id='si1.div']/div[3]/p").text
    assert t == "Bitte im WKZ melden"

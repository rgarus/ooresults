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
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
import web
from lxml import etree

import ooresults
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.result_type import SpStatus
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


S1 = datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
F1 = datetime(2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1)))
C1 = datetime(2020, 2, 9, 10, 8, 21, tzinfo=timezone(timedelta(hours=1)))
C2 = datetime(2020, 2, 9, 10, 12, 0, tzinfo=timezone(timedelta(hours=1)))
C3 = datetime(2020, 2, 9, 10, 13, 38, tzinfo=timezone(timedelta(hours=1)))
C4 = datetime(2020, 2, 9, 10, 18, 56, tzinfo=timezone(timedelta(hours=1)))
C5 = datetime(2020, 2, 9, 10, 26, 33, tzinfo=timezone(timedelta(hours=1)))


@pytest.fixture()
def entry() -> EntryType:
    return EntryType(
        id=11,
        event_id=2,
        competitor_id=None,
        first_name=None,
        last_name=None,
    )


@pytest.fixture()
def person_race_result() -> PersonRaceResult:
    return PersonRaceResult(
        start_time=S1,
        punched_start_time=S1,
        si_punched_start_time=S1,
        finish_time=F1,
        punched_finish_time=F1,
        si_punched_finish_time=F1,
        status=ResultStatus.OK,
        time=2001,
        split_times=[
            SplitTime(
                control_code="31",
                punch_time=None,
                si_punch_time=None,
                status=SpStatus.MISSING,
                time=None,
            ),
            SplitTime(
                control_code="32",
                punch_time=None,
                si_punch_time=C2,
                status=SpStatus.MISSING,
                time=None,
            ),
            SplitTime(
                control_code="31",
                punch_time=C3,
                si_punch_time=None,
                status=SpStatus.OK,
                time=818,
            ),
            SplitTime(
                control_code="33",
                punch_time=C4,
                si_punch_time=C4,
                status=SpStatus.OK,
                time=1136,
            ),
            SplitTime(
                control_code="31",
                punch_time=C5,
                si_punch_time=C5,
                status=SpStatus.ADDITIONAL,
                time=1593,
            ),
        ],
    )


def test_without_competitor_and_without_punches(render, entry: EntryType):
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    input_id = html.find(".//input[@id='entr.spId']")
    assert input_id.attrib["name"] == "entry_id"
    assert input_id.attrib["value"] == "11"
    assert input_id.attrib["hidden"] == ""

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert len(tds) == 9
    assert tds[0].text is None
    assert tds[1].text is None
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None
    assert tds[7].text is None
    assert tds[8].text is None

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    assert len(rows) == 1

    # stop time
    tds = rows[0].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "Finish"
    assert tds[1].text == "Finish"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None


def test_with_competitor_but_without_punches(render, entry: EntryType):
    entry.competitor_id = 25
    entry.first_name = "Angela"
    entry.last_name = "Merkel"
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    input_id = html.find(".//input[@id='entr.spId']")
    assert input_id.attrib["name"] == "entry_id"
    assert input_id.attrib["value"] == "11"
    assert input_id.attrib["hidden"] == ""

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert len(tds) == 9
    assert tds[0].text == "Angela"
    assert tds[1].text == "Merkel"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None
    assert tds[7].text is None
    assert tds[8].text is None

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    assert len(rows) == 2

    # start time
    tds = rows[0].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Start"
    assert tds[1].text == "Start"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_start"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(-1)"

    # stop time
    tds = rows[1].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Finish"
    assert tds[1].text == "Finish"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_finish"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(-2)"


def test_first_name_is_defined(render, entry: EntryType):
    entry.first_name = "Angela"
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[0].text == "Angela"


def test_last_name_is_defined(render, entry: EntryType):
    entry.last_name = "Merkel"
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[1].text == "Merkel"


def test_year_is_defined(render, entry: EntryType):
    entry.year = 1957
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[2].text == "1957"


def test_class_name_is_defined(render, entry: EntryType):
    entry.class_name = "Elite Women"
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[3].text == "Elite Women"


def test_chip_is_defined(render, entry: EntryType):
    entry.chip = "1234567"
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[4].text == "1234567"


def test_start_time_is_defined(render, entry: EntryType):
    entry.result.start_time = S1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[5].text == "10:00:00"


def test_finish_time_is_defined(render, entry: EntryType):
    entry.result.finish_time = F1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[6].text == "10:33:21"


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
def test_status_is_defined(render, entry: EntryType, status: ResultStatus, text: str):
    entry.result.status = status
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[7].text == text


def test_time_is_defined(render, entry: EntryType):
    entry.result.time = 2001
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    tds = html.findall(".//form[@id='entr.formSplitTimes']/table[1]//td")
    assert tds[8].text == "33:21"


def test_clear_time_is_defined_and_without_competitor(render, entry: EntryType):
    entry.result.punched_clear_time = C1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    # rows Clear, Finish
    assert len(rows) == 2

    # clear time
    tds = rows[0].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "Clear"
    assert tds[1].text == "Clear"
    assert tds[2].text == "10:08:21"
    assert tds[3].text == "10:08:21"
    assert tds[4].text is None
    assert tds[5].text is None


def test_clear_time_is_defined_and_with_competitor(render, entry: EntryType):
    entry.competitor_id = 25
    entry.result.punched_clear_time = C1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    # rows Clear, Start, Finish
    assert len(rows) == 3

    # clear time
    tds = rows[0].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Clear"
    assert tds[1].text == "Clear"
    assert tds[2].text == "10:08:21"
    assert tds[3].text == "10:08:21"
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None


def test_check_time_is_defined_and_without_competitor(render, entry: EntryType):
    entry.result.punched_check_time = C1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    # rows Check, Finish
    assert len(rows) == 2

    # check time
    tds = rows[0].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "Check"
    assert tds[1].text == "Check"
    assert tds[2].text == "10:08:21"
    assert tds[3].text == "10:08:21"
    assert tds[4].text is None
    assert tds[5].text is None


def test_check_time_is_defined_and_with_competitor(render, entry: EntryType):
    entry.competitor_id = 25
    entry.result.punched_check_time = C1
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    # rows Check, Start, Finish
    assert len(rows) == 3

    # check time
    tds = rows[0].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Check"
    assert tds[1].text == "Check"
    assert tds[2].text == "10:08:21"
    assert tds[3].text == "10:08:21"
    assert tds[4].text is None
    assert tds[5].text is None
    assert tds[6].text is None


def test_without_competitor_but_with_punches(
    render, entry: EntryType, person_race_result: PersonRaceResult
):
    entry.result = person_race_result
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    assert len(rows) == 7

    # start time
    tds = rows[0].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "Start"
    assert tds[1].text == "Start"
    assert tds[2].text == "10:00:00"
    assert tds[3].text == "10:00:00"
    assert tds[4].text is None
    assert tds[5].text == "0:00"

    # stop time
    tds = rows[1].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "Finish"
    assert tds[1].text == "Finish"
    assert tds[2].text == "10:33:21"
    assert tds[3].text == "10:33:21"
    assert tds[4].text is None
    assert tds[5].text == "33:21"

    # control 1
    tds = rows[2].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "1"
    assert tds[1].text == "31"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None

    # control 2
    tds = rows[3].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "2"
    assert tds[1].text == "32"
    assert tds[2].text == "10:12:00"
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None

    # control 3
    tds = rows[4].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "3"
    assert tds[1].text == "31"
    assert tds[2].text is None
    assert tds[3].text == "10:13:38"
    assert tds[4].text is None
    assert tds[5].text == "13:38"

    # control 4
    tds = rows[5].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text == "4"
    assert tds[1].text == "33"
    assert tds[2].text == "10:18:56"
    assert tds[3].text == "10:18:56"
    assert tds[4].text is None
    assert tds[5].text == "18:56"

    # control 5
    tds = rows[6].findall(".//td")
    assert len(tds) == 6
    assert tds[0].text is None
    assert tds[1].text == "31"
    assert tds[2].text == "10:26:33"
    assert tds[3].text == "10:26:33"
    assert tds[4].text is None
    assert tds[5].text == "26:33"


def test_with_competitor_and_with_punches(
    render, entry: EntryType, person_race_result: PersonRaceResult
):
    entry.competitor_id = 25
    entry.result = person_race_result
    html = etree.HTML(str(render.add_entry_result(entry=entry)))

    rows = html.findall(".//form[@id='entr.formSplitTimes']/table[2]/tbody/tr")
    assert len(rows) == 7

    # start time
    tds = rows[0].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Start"
    assert tds[1].text == "Start"
    assert tds[2].text == "10:00:00"
    assert tds[3].text == "10:00:00"
    assert tds[4].text is None
    assert tds[5].text == "0:00"
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_start"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(-1)"

    # stop time
    tds = rows[1].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "Finish"
    assert tds[1].text == "Finish"
    assert tds[2].text == "10:33:21"
    assert tds[3].text == "10:33:21"
    assert tds[4].text is None
    assert tds[5].text == "33:21"
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_finish"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(-2)"

    # control 1
    tds = rows[2].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "1"
    assert tds[1].text == "31"
    assert tds[2].text is None
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_0"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(0)"

    # control 2
    tds = rows[3].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "2"
    assert tds[1].text == "32"
    assert tds[2].text == "10:12:00"
    assert tds[3].text is None
    assert tds[4].text is None
    assert tds[5].text is None
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_1"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(1)"

    # control 3
    tds = rows[4].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "3"
    assert tds[1].text == "31"
    assert tds[2].text is None
    assert tds[3].text == "10:13:38"
    assert tds[4].text is None
    assert tds[5].text == "13:38"
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_2"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(2)"

    # control 4
    tds = rows[5].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text == "4"
    assert tds[1].text == "33"
    assert tds[2].text == "10:18:56"
    assert tds[3].text == "10:18:56"
    assert tds[4].text is None
    assert tds[5].text == "18:56"
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_3"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(3)"

    # control 5
    tds = rows[6].findall(".//td")
    assert len(tds) == 7
    assert tds[0].text is None
    assert tds[1].text == "31"
    assert tds[2].text == "10:26:33"
    assert tds[3].text == "10:26:33"
    assert tds[4].text is None
    assert tds[5].text == "26:33"
    inp = tds[6].find("./input")
    assert inp.attrib["name"] == "edit_4"
    assert inp.attrib["onclick"] == "entr_myPunchEdit(4)"

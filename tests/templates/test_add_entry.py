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
from datetime import timezone
from datetime import timedelta
from typing import List
from typing import Dict

import pytest
import web
from lxml import etree

import ooresults
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassType
from ooresults.repo.club_type import ClubType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.repo.start_type import PersonRaceStart
from ooresults.utils.globals import t_globals


S1 = datetime(2021, 8, 19, 18, 43, 33, tzinfo=timezone(timedelta(hours=2)))


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


@pytest.fixture()
def classes() -> List[ClassType]:
    return [
        ClassType(
            id=7,
            event_id=1,
            name="Elite Men",
            short_name="E Men",
            course_id=2,
            params=ClassParams(),
        ),
        ClassType(
            id=8,
            event_id=1,
            name="Elite Women",
            short_name="E Women",
            course_id=2,
            params=ClassParams(),
        ),
    ]


@pytest.fixture()
def clubs() -> List[ClubType]:
    return [
        ClubType(
            id=3,
            name="OC Bundestag",
        ),
        ClubType(
            id=2,
            name="OL Bundestag",
        ),
    ]


@pytest.fixture()
def not_assigned_results() -> List[Dict]:
    return [
        {"key": 15, "value": "15:34:12   --   34578"},
        {"key": 37, "value": "15:18:19   --   34578"},
        {"key": 26, "value": "16:00:11   --   8123599"},
    ]


@pytest.fixture()
def event_fields() -> List[str]:
    return []


def test_add_entry_for_add(
    render,
    classes: List[ClassType],
    clubs: List[ClubType],
):
    entry = None
    html = etree.HTML(
        str(
            render.add_entry(
                entry=entry,
                classes=classes,
                clubs=clubs,
                results=[],
                event_fields=[],
            )
        )
    )

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == ""

    input_competitor_id = html.find(".//input[@name='competitor_id']")
    assert input_competitor_id.attrib["value"] == ""

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == ""
    assert html.find(".//input[@name='first_name']/../button").text == "Competitors ..."

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == ""

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": "", "selected": "selected"}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == ""

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == ""

    option_club_id = html.findall(".//select[@name='club_id']/option")
    assert len(option_club_id) == 3
    assert option_club_id[0].attrib == {"value": ""}
    assert option_club_id[0].text is None
    assert option_club_id[1].attrib == {"value": "3"}
    assert option_club_id[1].text == "OC Bundestag"
    assert option_club_id[2].attrib == {"value": "2"}
    assert option_club_id[2].text == "OL Bundestag"

    option_class_id = html.findall(".//select[@name='class_id']/option")
    assert len(option_class_id) == 2
    assert option_class_id[0].attrib == {"value": "7"}
    assert option_class_id[0].text == "Elite Men"
    assert option_class_id[1].attrib == {"value": "8"}
    assert option_class_id[1].text == "Elite Women"

    input_not_competing = html.find(".//input[@name='not_competing']")
    assert input_not_competing.attrib["value"] == "true"
    assert "checked" not in input_not_competing.attrib

    input_start_time = html.find(".//input[@name='start_time']")
    assert input_start_time.attrib["value"] == ""

    option_status = html.findall(".//select[@name='status']/option")
    assert len(option_status) == 9
    assert option_status[0].attrib == {"value": "0", "selected": "selected"}
    assert option_status[0].text is None
    assert option_status[1].attrib == {"value": "1"}
    assert option_status[1].text == "Started"
    assert option_status[2].attrib == {"value": "2"}
    assert option_status[2].text == "Finished"
    assert option_status[3].attrib == {"value": "3"}
    assert option_status[3].text == "OK"
    assert option_status[4].attrib == {"value": "4"}
    assert option_status[4].text == "MP"
    assert option_status[5].attrib == {"value": "5"}
    assert option_status[5].text == "DNS"
    assert option_status[6].attrib == {"value": "6"}
    assert option_status[6].text == "DNF"
    assert option_status[7].attrib == {"value": "7"}
    assert option_status[7].text == "OTL"
    assert option_status[8].attrib == {"value": "8"}
    assert option_status[8].text == "DSQ"

    assert html.findall(".//select[@name='result']/option") == []


def test_add_entry_for_edit_without_results(
    render,
    classes: List[ClassType],
    clubs: List[ClubType],
):
    entry = EntryType(
        id=11,
        event_id=2,
        competitor_id=3,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=8,
        class_name="Elite Women",
        not_competing=False,
        chip="9999999",
        fields={},
        result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
        start=PersonRaceStart(start_time=S1),
        club_id=2,
        club_name="OL Bundestag",
    )
    html = etree.HTML(
        str(
            render.add_entry(
                entry=entry,
                classes=classes,
                clubs=clubs,
                results=[],
                event_fields=[],
            )
        )
    )

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "11"

    input_competitor_id = html.find(".//input[@name='competitor_id']")
    assert input_competitor_id.attrib["value"] == "3"

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == "Angela"
    assert html.find(".//input[@name='first_name']/../button") is None

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == "Merkel"

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F", "selected": "selected"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == "1957"

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == "9999999"

    option_club_id = html.findall(".//select[@name='club_id']/option")
    assert len(option_club_id) == 3
    assert option_club_id[0].attrib == {"value": ""}
    assert option_club_id[0].text is None
    assert option_club_id[1].attrib == {"value": "3"}
    assert option_club_id[1].text == "OC Bundestag"
    assert option_club_id[2].attrib == {"value": "2", "selected": "selected"}
    assert option_club_id[2].text == "OL Bundestag"

    option_class_id = html.findall(".//select[@name='class_id']/option")
    assert len(option_class_id) == 2
    assert option_class_id[0].attrib == {"value": "7"}
    assert option_class_id[0].text == "Elite Men"
    assert option_class_id[1].attrib == {"value": "8", "selected": "selected"}
    assert option_class_id[1].text == "Elite Women"

    input_not_competing = html.find(".//input[@name='not_competing']")
    assert input_not_competing.attrib["value"] == "true"
    assert "checked" not in input_not_competing.attrib

    input_start_time = html.find(".//input[@name='start_time']")
    assert input_start_time.attrib["value"] == "18:43:33"

    option_status = html.findall(".//select[@name='status']/option")
    assert len(option_status) == 9
    assert option_status[0].attrib == {"value": "0"}
    assert option_status[0].text is None
    assert option_status[1].attrib == {"value": "1"}
    assert option_status[1].text == "Started"
    assert option_status[2].attrib == {"value": "2"}
    assert option_status[2].text == "Finished"
    assert option_status[3].attrib == {"value": "3"}
    assert option_status[3].text == "OK"
    assert option_status[4].attrib == {"value": "4"}
    assert option_status[4].text == "MP"
    assert option_status[5].attrib == {"value": "5", "selected": "selected"}
    assert option_status[5].text == "DNS"
    assert option_status[6].attrib == {"value": "6"}
    assert option_status[6].text == "DNF"
    assert option_status[7].attrib == {"value": "7"}
    assert option_status[7].text == "OTL"
    assert option_status[8].attrib == {"value": "8"}
    assert option_status[8].text == "DSQ"

    assert html.findall(".//select[@name='result']/option") == []


def test_add_entry_for_edit_with_results(
    render,
    classes: List[ClassType],
    clubs: List[ClubType],
    not_assigned_results: List[Dict],
):
    entry = EntryType(
        id=11,
        event_id=2,
        competitor_id=3,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=8,
        class_name="Elite Women",
        not_competing=True,
        chip="9999999",
        fields={},
        result=PersonRaceResult(
            start_time=datetime(
                2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
            ),
            finish_time=datetime(
                2020, 2, 9, 10, 33, 21, tzinfo=timezone(timedelta(hours=1))
            ),
            status=ResultStatus.OK,
            time=2001,
            split_times=[
                SplitTime(control_code="31", status=SpStatus.OK, time=501),
                SplitTime(control_code="32", status=SpStatus.OK, time=720),
                SplitTime(control_code="31", status=SpStatus.OK, time=818),
                SplitTime(control_code="33", status=SpStatus.OK, time=1136),
                SplitTime(control_code="31", status=SpStatus.OK, time=1593),
            ],
        ),
        start=PersonRaceStart(start_time=S1),
        club_id=2,
        club_name="OL Bundestag",
    )
    html = etree.HTML(
        str(
            render.add_entry(
                entry=entry,
                classes=classes,
                clubs=clubs,
                results=[{"key": -1, "value": "Remove result"}] + not_assigned_results,
                event_fields=[],
            )
        )
    )

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "11"

    input_competitor_id = html.find(".//input[@name='competitor_id']")
    assert input_competitor_id.attrib["value"] == "3"

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == "Angela"
    assert html.find(".//input[@name='first_name']/../button") is None

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == "Merkel"

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F", "selected": "selected"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == "1957"

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == "9999999"

    option_club_id = html.findall(".//select[@name='club_id']/option")
    assert len(option_club_id) == 3
    assert option_club_id[0].attrib == {"value": ""}
    assert option_club_id[0].text is None
    assert option_club_id[1].attrib == {"value": "3"}
    assert option_club_id[1].text == "OC Bundestag"
    assert option_club_id[2].attrib == {"value": "2", "selected": "selected"}
    assert option_club_id[2].text == "OL Bundestag"

    option_class_id = html.findall(".//select[@name='class_id']/option")
    assert len(option_class_id) == 2
    assert option_class_id[0].attrib == {"value": "7"}
    assert option_class_id[0].text == "Elite Men"
    assert option_class_id[1].attrib == {"value": "8", "selected": "selected"}
    assert option_class_id[1].text == "Elite Women"

    input_not_competing = html.find(".//input[@name='not_competing']")
    assert input_not_competing.attrib["value"] == "true"
    assert input_not_competing.attrib["checked"] == "checked"

    input_start_time = html.find(".//input[@name='start_time']")
    assert input_start_time.attrib["value"] == "18:43:33"

    option_status = html.findall(".//select[@name='status']/option")
    assert len(option_status) == 6
    assert option_status[0].attrib == {"value": "2"}
    assert option_status[0].text == "Finished"
    assert option_status[1].attrib == {"value": "3", "selected": "selected"}
    assert option_status[1].text == "OK"
    assert option_status[2].attrib == {"value": "4"}
    assert option_status[2].text == "MP"
    assert option_status[3].attrib == {"value": "6"}
    assert option_status[3].text == "DNF"
    assert option_status[4].attrib == {"value": "7"}
    assert option_status[4].text == "OTL"
    assert option_status[5].attrib == {"value": "8"}
    assert option_status[5].text == "DSQ"

    option_result = html.findall(".//select[@name='result']/option")
    assert len(option_result) == 5
    assert option_result[0].attrib == {"value": "", "selected": "selected"}
    assert option_result[0].text is None
    assert option_result[1].attrib == {"value": "-1"}
    assert option_result[1].text == "Remove result"
    assert option_result[2].attrib == {"value": "15"}
    assert option_result[2].text == "15:34:12   --   34578"
    assert option_result[3].attrib == {"value": "37"}
    assert option_result[3].text == "15:18:19   --   34578"
    assert option_result[4].attrib == {"value": "26"}
    assert option_result[4].text == "16:00:11   --   8123599"


def test_add_entry_for_edit_with_additional_fields(
    render,
    classes: List[ClassType],
):
    entry = EntryType(
        id=11,
        event_id=2,
        competitor_id=3,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=8,
        class_name="Elite Women",
        not_competing=False,
        chip="9999999",
        fields={0: "1024", 1: "Thüringen"},
        result=PersonRaceResult(),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )
    html = etree.HTML(
        str(
            render.add_entry(
                entry=entry,
                classes=classes,
                clubs=[],
                results=[],
                event_fields=["Number", "Region"],
            )
        )
    )

    input_id = html.find(".//input[@name='id']")
    assert input_id.attrib["value"] == "11"

    input_competitor_id = html.find(".//input[@name='competitor_id']")
    assert input_competitor_id.attrib["value"] == "3"

    input_first_name = html.find(".//input[@name='first_name']")
    assert input_first_name.attrib["value"] == "Angela"
    assert html.find(".//input[@name='first_name']/../button") is None

    input_last_name = html.find(".//input[@name='last_name']")
    assert input_last_name.attrib["value"] == "Merkel"

    options_gender = html.findall(".//select[@name='gender']/option")
    assert len(options_gender) == 3
    assert options_gender[0].attrib == {"value": ""}
    assert options_gender[0].text is None
    assert options_gender[1].attrib == {"value": "F", "selected": "selected"}
    assert options_gender[1].text == "F"
    assert options_gender[2].attrib == {"value": "M"}
    assert options_gender[2].text == "M"

    input_year = html.find(".//input[@name='year']")
    assert input_year.attrib["value"] == "1957"

    input_chip = html.find(".//input[@name='chip']")
    assert input_chip.attrib["value"] == "9999999"

    option_club_id = html.findall(".//select[@name='club_id']/option")
    assert len(option_club_id) == 1
    assert option_club_id[0].attrib == {"value": "", "selected": "selected"}
    assert option_club_id[0].text is None

    option_class_id = html.findall(".//select[@name='class_id']/option")
    assert len(option_class_id) == 2
    assert option_class_id[0].attrib == {"value": "7"}
    assert option_class_id[0].text == "Elite Men"
    assert option_class_id[1].attrib == {"value": "8", "selected": "selected"}
    assert option_class_id[1].text == "Elite Women"

    input_chip = html.find(".//input[@name='f0']")
    assert input_chip.attrib["value"] == "1024"

    input_chip = html.find(".//input[@name='f1']")
    assert input_chip.attrib["value"] == "Thüringen"

    input_not_competing = html.find(".//input[@name='not_competing']")
    assert input_not_competing.attrib["value"] == "true"
    assert "checked" not in input_not_competing.attrib

    input_start_time = html.find(".//input[@name='start_time']")
    assert input_start_time.attrib["value"] == ""

    option_status = html.findall(".//select[@name='status']/option")
    assert len(option_status) == 9
    assert option_status[0].attrib == {"value": "0", "selected": "selected"}
    assert option_status[0].text is None
    assert option_status[1].attrib == {"value": "1"}
    assert option_status[1].text == "Started"
    assert option_status[2].attrib == {"value": "2"}
    assert option_status[2].text == "Finished"
    assert option_status[3].attrib == {"value": "3"}
    assert option_status[3].text == "OK"
    assert option_status[4].attrib == {"value": "4"}
    assert option_status[4].text == "MP"
    assert option_status[5].attrib == {"value": "5"}
    assert option_status[5].text == "DNS"
    assert option_status[6].attrib == {"value": "6"}
    assert option_status[6].text == "DNF"
    assert option_status[7].attrib == {"value": "7"}
    assert option_status[7].text == "OTL"
    assert option_status[8].attrib == {"value": "8"}
    assert option_status[8].text == "DSQ"

    assert html.findall(".//select[@name='result']/option") == []

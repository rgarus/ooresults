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


import copy
import datetime
from typing import Dict

import pytest

from ooresults.repo import repo
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo.start_type import PersonRaceStart
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.handler import model


entry_time = datetime.datetime(2015, 1, 1, 13, 38, 59, tzinfo=datetime.timezone.utc)
s1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=datetime.timezone.utc)
c1 = datetime.datetime(2015, 1, 1, 12, 39, 1, tzinfo=datetime.timezone.utc)
c2 = datetime.datetime(2015, 1, 1, 12, 39, 3, tzinfo=datetime.timezone.utc)
c3 = datetime.datetime(2015, 1, 1, 12, 39, 5, tzinfo=datetime.timezone.utc)
f1 = datetime.datetime(2015, 1, 1, 12, 39, 7, tzinfo=datetime.timezone.utc)


def t(a: datetime, b: datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


@pytest.fixture
def db():
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def event_id(db):
    return db.add_event(
        name="Event",
        date=datetime.date(year=2015, month=1, day=1),
        key="4711",
        publish=False,
        series=None,
    )


@pytest.fixture
def course_id(db, event_id):
    return db.add_course(
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


@pytest.fixture
def class_id(db, event_id, course_id):
    return db.add_class(
        event_id=event_id,
        name="Elite",
        short_name="E",
        course_id=course_id,
        params=ClassParams(),
    )


@pytest.fixture
def class_id_without_course(db, event_id):
    return db.add_class(
        event_id=event_id,
        name="Elite",
        short_name="E",
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def entry_1(db, event_id, class_id):
    id = db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Robert",
        last_name="Lewandowski",
        gender="",
        year=None,
        class_id=class_id,
        club_id=None,
        not_competing=False,
        chip="12734",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    entry = db.get_entry(id=id)[0]
    return copy.deepcopy(entry)


@pytest.fixture
def entry_1_without_course(db, event_id, class_id_without_course):
    id = db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Robert",
        last_name="Lewandowski",
        gender="",
        year=None,
        class_id=class_id_without_course,
        club_id=None,
        not_competing=False,
        chip="12734",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    entry = db.get_entry(id=id)[0]
    return copy.deepcopy(entry)


@pytest.fixture
def entry_2(db, event_id, class_id):
    id = db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Yogi",
        last_name="Löw",
        gender="N",
        year=None,
        class_id=class_id,
        club_id=None,
        not_competing=False,
        chip="7410",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    entry = db.get_entry(id=id)[0]
    return copy.deepcopy(entry)


@pytest.fixture
def entry_2_with_result(db, event_id, class_id, entry_2):
    db.update_entry_result(
        id=entry_2["id"],
        chip=entry_2["chip"],
        start_time=entry_2["start"].start_time,
        result=PersonRaceResult(
            status=ResultStatus.OK,
            start_time=s1,
            finish_time=f1,
            punched_start_time=s1,
            punched_finish_time=f1,
            time=t(s1, f1),
            split_times=[
                SplitTime(
                    control_code="101", punch_time=c1, time=t(s1, c1), status="OK"
                ),
                SplitTime(
                    control_code="102", punch_time=c2, time=t(s1, c2), status="OK"
                ),
                SplitTime(
                    control_code="103", punch_time=c3, time=t(s1, c3), status="OK"
                ),
            ],
        ),
    )
    entry = db.get_entry(id=entry_2["id"])[0]
    return copy.deepcopy(entry)


@pytest.fixture
def entry_3(db, event_id, class_id):
    id = db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_id,
        club_id=None,
        not_competing=False,
        chip="12734",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    entry = db.get_entry(id=id)[0]
    return copy.deepcopy(entry)


@pytest.fixture
def unassigned_entry(db, event_id):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    id = db.add_entry_result(
        event_id=event_id,
        chip="7410",
        result=result,
        start_time=None,
    )
    entry = db.get_entry(id=id)[0]
    return copy.deepcopy(entry)


def assert_entries_are_equal(entry_a: Dict, entry_b: Dict) -> None:
    assert entry_a["id"] == entry_b["id"]
    assert entry_a["event_id"] == entry_b["event_id"]
    assert entry_a["first_name"] == entry_b["first_name"]
    assert entry_a["last_name"] == entry_b["last_name"]
    assert entry_a["gender"] == entry_b["gender"]
    assert entry_a["year"] == entry_b["year"]
    assert entry_a["competitor_id"] == entry_b["competitor_id"]
    assert entry_a["not_competing"] == entry_b["not_competing"]
    assert entry_a["chip"] == entry_b["chip"]
    assert entry_a["fields"] == entry_b["fields"]
    assert entry_a["result"] == entry_b["result"]
    assert entry_a["start"] == entry_b["start"]
    assert entry_a["club_id"] == entry_b["club_id"]
    assert entry_a["club"] == entry_b["club"]
    assert entry_a["class_id"] == entry_b["class_id"]
    assert entry_a["class_"] == entry_b["class_"]
    assert entry_a.get("missingControls", None) == entry_b.get("missingControls", None)


def test_assign_to_entry_if_cardnumber_is_unique(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.OK,
        "time": t(s1, f1),
        "error": None,
        "missingControls": [],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    entry_2["result"] = PersonRaceResult(
        status=ResultStatus.OK,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=t(s1, c1), status="OK"),
            SplitTime(control_code="102", punch_time=c2, time=t(s1, c2), status="OK"),
            SplitTime(control_code="103", punch_time=c3, time=t(s1, c3), status="OK"),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_assign_to_entry_if_cardnumber_is_unique_but_finish_time_is_missing(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=None,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.DID_NOT_FINISH,
        "time": None,
        "error": None,
        "missingControls": ["FINISH"],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    entry_2["result"] = PersonRaceResult(
        status=ResultStatus.DID_NOT_FINISH,
        start_time=s1,
        finish_time=None,
        punched_start_time=s1,
        punched_finish_time=None,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=t(s1, c1), status="OK"),
            SplitTime(control_code="102", punch_time=c2, time=t(s1, c2), status="OK"),
            SplitTime(control_code="103", punch_time=c3, time=t(s1, c3), status="OK"),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_assign_to_entry_if_cardnumber_is_unique_but_start_time_is_missing(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.MISSING_PUNCH,
        "time": None,
        "error": None,
        "missingControls": ["START"],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    entry_2["result"] = PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH,
        start_time=None,
        finish_time=f1,
        punched_start_time=None,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=None, status="OK"),
            SplitTime(control_code="102", punch_time=c2, time=None, status="OK"),
            SplitTime(control_code="103", punch_time=c3, time=None, status="OK"),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_assign_to_entry_if_cardnumber_is_unique_but_controls_are_missing(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.MISSING_PUNCH,
        "time": t(s1, f1),
        "error": None,
        "missingControls": ["102", "103"],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    entry_2["result"] = PersonRaceResult(
        status=ResultStatus.MISSING_PUNCH,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=t(s1, c1), status="OK"),
            SplitTime(control_code="102", punch_time=None, time=None, status="Missing"),
            SplitTime(control_code="103", punch_time=None, time=None, status="Missing"),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_assign_to_entry_and_delete_unnamed_entry_with_same_result(
    db, event_id, entry_1, entry_2, entry_3, unassigned_entry
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)
    print(res)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.OK,
        "time": t(s1, f1),
        "error": None,
        "missingControls": [],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    entry_2["result"] = PersonRaceResult(
        status=ResultStatus.OK,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(control_code="101", punch_time=c1, time=t(s1, c1), status="OK"),
            SplitTime(control_code="102", punch_time=c2, time=t(s1, c2), status="OK"),
            SplitTime(control_code="103", punch_time=c3, time=t(s1, c3), status="OK"),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_store_as_new_entry_if_another_result_exists(
    db, event_id, entry_1, entry_2, entry_3, unassigned_entry
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "There are other results for this card",
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 5

    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status="Additional"
            ),
        ],
    )
    new_entry = {
        "id": [
            e["id"]
            for e in entries
            if e["id"]
            not in [entry_1["id"], entry_2["id"], entry_3["id"], unassigned_entry["id"]]
        ][0],
        "event_id": event_id,
        "first_name": None,
        "last_name": None,
        "gender": None,
        "year": None,
        "competitor_id": None,
        "not_competing": False,
        "chip": "7410",
        "fields": {},
        "result": result,
        "start": PersonRaceStart(),
        "club_id": None,
        "club": None,
        "class_id": None,
        "class_": None,
    }

    assert_entries_are_equal(entry_a=entries[0], entry_b=unassigned_entry)
    assert_entries_are_equal(entry_a=entries[1], entry_b=new_entry)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[3], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[4], entry_b=entry_3)


def test_do_not_store_as_new_entry_if_result_already_exists(
    db, event_id, entry_1, entry_3, unassigned_entry
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "Control card unknown",
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    assert_entries_are_equal(entry_a=entries[0], entry_b=unassigned_entry)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_store_as_new_entry_if_cardnumber_is_unknown(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "999999",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "999999",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "Control card unknown",
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 4

    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status="Additional"
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status="Additional"
            ),
        ],
    )
    new_entry = {
        "id": [
            e["id"]
            for e in entries
            if e["id"] not in [entry_1["id"], entry_2["id"], entry_3["id"]]
        ][0],
        "event_id": event_id,
        "first_name": None,
        "last_name": None,
        "gender": None,
        "year": None,
        "competitor_id": None,
        "not_competing": False,
        "chip": "999999",
        "fields": {},
        "result": result,
        "start": PersonRaceStart(),
        "club_id": None,
        "club": None,
        "class_id": None,
        "class_": None,
    }

    assert_entries_are_equal(entry_a=entries[0], entry_b=new_entry)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[3], entry_b=entry_3)


def test_store_as_new_entry_if_cardnumber_exist_several_times(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "12734",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "12734",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "There are several entries for this card",
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 4

    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status="Additional"
            ),
            SplitTime(
                control_code="103", punch_time=c3, time=t(s1, c3), status="Additional"
            ),
        ],
    )
    new_entry = {
        "id": [
            e["id"]
            for e in entries
            if e["id"] not in [entry_1["id"], entry_2["id"], entry_3["id"]]
        ][0],
        "event_id": event_id,
        "first_name": None,
        "last_name": None,
        "gender": None,
        "year": None,
        "competitor_id": None,
        "not_competing": False,
        "chip": "12734",
        "fields": {},
        "result": result,
        "start": PersonRaceStart(),
        "club_id": None,
        "club": None,
        "class_id": None,
        "class_": None,
    }

    assert_entries_are_equal(entry_a=entries[0], entry_b=new_entry)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[3], entry_b=entry_3)


def test_use_already_assigned_entry_if_it_has_the_same_result(
    db, event_id, entry_1, entry_2_with_result, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": "Yogi",
        "lastName": "Löw",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.OK,
        "time": t(s1, f1),
        "error": None,
        "missingControls": [],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2_with_result)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)


def test_store_as_new_entry_if_cardnumber_is_unique_with_another_result(
    db, event_id, entry_1, entry_2_with_result, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="109", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "7410",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": ResultStatus.FINISHED,
        "time": None,
        "error": "There are other results for this card",
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 4

    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status="Additional"
            ),
            SplitTime(
                control_code="109", punch_time=c3, time=t(s1, c3), status="Additional"
            ),
        ],
    )
    new_entry = {
        "id": [
            e["id"]
            for e in entries
            if e["id"] not in [entry_1["id"], entry_2_with_result["id"], entry_3["id"]]
        ][0],
        "event_id": event_id,
        "first_name": None,
        "last_name": None,
        "gender": None,
        "year": None,
        "competitor_id": None,
        "not_competing": False,
        "chip": "7410",
        "fields": {},
        "result": result,
        "start": PersonRaceStart(),
        "club_id": None,
        "club": None,
        "class_id": None,
        "class_": None,
    }

    assert_entries_are_equal(entry_a=entries[0], entry_b=new_entry)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_2_with_result)
    assert_entries_are_equal(entry_a=entries[3], entry_b=entry_3)


def test_use_empty_control_list_if_course_is_undefined(
    db, event_id, entry_1_without_course
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="109", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "12734",
        "result": result,
    }

    status, event, res = model.store_cardreader_result(event_key="4711", item=item)

    assert status == "cardRead"
    assert event["id"] == event_id
    assert res == {
        "entryTime": entry_time,
        "eventId": event_id,
        "controlCard": "12734",
        "firstName": "Robert",
        "lastName": "Lewandowski",
        "club": None,
        "class": "Elite",
        "status": ResultStatus.FINISHED,
        "time": t(s1, f1),
        "error": None,
        "missingControls": [],
    }

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 1

    entry_1_without_course["result"] = PersonRaceResult(
        status=ResultStatus.FINISHED,
        start_time=s1,
        finish_time=f1,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=t(s1, f1),
        split_times=[
            SplitTime(
                control_code="101", punch_time=c1, time=t(s1, c1), status="Additional"
            ),
            SplitTime(
                control_code="102", punch_time=c2, time=t(s1, c2), status="Additional"
            ),
            SplitTime(
                control_code="109", punch_time=c3, time=t(s1, c3), status="Additional"
            ),
        ],
    )

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1_without_course)


def test_raise_exception_if_event_key_is_unknown(
    db, event_id, entry_1, entry_2, entry_3
):
    result = PersonRaceResult(
        status=ResultStatus.FINISHED,
        punched_start_time=s1,
        punched_finish_time=f1,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=c1, status="Additional"),
            SplitTime(control_code="102", punch_time=c2, status="Additional"),
            SplitTime(control_code="103", punch_time=c3, status="Additional"),
        ],
    )
    item = {
        "entryType": "cardRead",
        "entryTime": entry_time,
        "controlCard": "7410",
        "result": result,
    }

    with pytest.raises(repo.EventNotFoundError, match='Event for key "4712" not found'):
        status, event, res = model.store_cardreader_result(event_key="4712", item=item)

    entries = db.get_entries(event_id=event_id)
    assert len(entries) == 3

    assert_entries_are_equal(entry_a=entries[0], entry_b=entry_1)
    assert_entries_are_equal(entry_a=entries[1], entry_b=entry_2)
    assert_entries_are_equal(entry_a=entries[2], entry_b=entry_3)

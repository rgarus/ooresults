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

import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.handler import model


@pytest.fixture
def db():
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def event(db):
    id = db.add_event(
        name="Event",
        date=datetime.date(year=2015, month=1, day=1),
        key="4711",
        publish=False,
        series=None,
    )
    item = db.get_event(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def course_a(db, event):
    id = db.add_course(
        event_id=event["id"],
        name="Bahn A",
        length=3700,
        climb=110,
        controls=["101", "102", "103", "104"],
    )
    item = db.get_course(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def course_b(db, event):
    id = db.add_course(
        event_id=event["id"],
        name="Bahn B",
        length=4500,
        climb=90,
        controls=["101", "103"],
    )
    item = db.get_course(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def class_a(db, event, course_a):
    id = db.add_class(
        event_id=event["id"],
        name="Bahn A - Lang",
        short_name="Bahn A - Lang",
        course_id=course_a["id"],
        params=ClassParams(),
    )
    item = db.get_class(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def class_b(db, event, course_b):
    id = db.add_class(
        event_id=event["id"],
        name="Bahn B - Mittel",
        short_name="Bahn B - Mittel",
        course_id=course_b["id"],
        params=ClassParams(),
    )
    item = db.get_class(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def entry_1(db, event, class_a):
    id = db.add_entry(
        event_id=event["id"],
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_a["id"],
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    db.update_entry_result(
        id=id,
        chip="7410",
        start_time=None,
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=9876,
        ),
    )
    item = db.get_entry(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def entry_2(db, event, class_b):
    id = db.add_entry(
        event_id=event["id"],
        competitor_id=None,
        first_name="Claudia",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_b["id"],
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    db.update_entry_result(
        id=id,
        chip="7411",
        start_time=None,
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
    )
    item = db.get_entry(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def entry_3(db, event, class_b):
    id = db.add_entry(
        event_id=event["id"],
        competitor_id=None,
        first_name="Birgit",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_b["id"],
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    db.update_entry_result(
        id=id,
        chip="7412",
        start_time=None,
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2113,
        ),
    )
    item = db.get_entry(id=id)[0]
    return copy.deepcopy(item)


@pytest.fixture
def entry_4(db, event, class_a):
    id = db.add_entry(
        event_id=event["id"],
        competitor_id=None,
        first_name="Birgit",
        last_name="Derkel",
        gender="",
        year=None,
        class_id=class_a["id"],
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    db.update_entry_result(
        id=id,
        chip="7413",
        start_time=None,
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=3333,
        ),
    )
    item = db.get_entry(id=id)[0]
    return copy.deepcopy(item)


def test_event_class_results(
    db, event, class_a, class_b, course_a, course_b, entry_1, entry_2, entry_3, entry_4
):
    m_event, m_class_results = model.event_class_results(event_id=event["id"])

    del class_a["event_id"]
    class_a["course"] = "Bahn A"
    class_a["course_length"] = 3700
    class_a["course_climb"] = 110
    class_a["number_of_controls"] = 4
    del class_b["event_id"]
    class_b["course"] = "Bahn B"
    class_b["course_length"] = 4500
    class_b["course_climb"] = 90
    class_b["number_of_controls"] = 2

    entry_1["rank"] = 2
    entry_1["time_behind"] = 9876 - 3333
    entry_1["points"] = 3333 / 9876
    entry_2["rank"] = 1
    entry_2["time_behind"] = 2001 - 2001
    entry_2["points"] = 2001 / 2001
    entry_3["rank"] = 2
    entry_3["time_behind"] = 2113 - 2001
    entry_3["points"] = 2001 / 2113
    entry_4["rank"] = 1
    entry_4["time_behind"] = 3333 - 3333
    entry_4["points"] = 3333 / 3333

    assert m_event == event
    assert m_class_results == [
        (
            class_a,
            [
                entry_4,
                entry_1,
            ],
        ),
        (
            class_b,
            [
                entry_2,
                entry_3,
            ],
        ),
    ]

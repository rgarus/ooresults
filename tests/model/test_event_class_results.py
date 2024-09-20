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
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.class_type import ClassType
from ooresults.repo.course_type import CourseType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.model import model


@pytest.fixture
def db():
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def event(db) -> EventType:
    id = db.add_event(
        name="Event",
        date=datetime.date(year=2015, month=1, day=1),
        key="4711",
        publish=False,
        series=None,
        fields=[],
    )
    item = db.get_event(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def course_a(db, event: EventType) -> CourseType:
    id = db.add_course(
        event_id=event.id,
        name="Bahn A",
        length=3700,
        climb=110,
        controls=["101", "102", "103", "104"],
    )
    item = db.get_course(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def course_b(db, event: EventType) -> CourseType:
    id = db.add_course(
        event_id=event.id,
        name="Bahn B",
        length=4500,
        climb=90,
        controls=["101", "103"],
    )
    item = db.get_course(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def class_a(db, event: EventType, course_a: CourseType) -> ClassType:
    id = db.add_class(
        event_id=event.id,
        name="Bahn A - Lang",
        short_name="Bahn A - Lang",
        course_id=course_a.id,
        params=ClassParams(),
    )
    item = db.get_class(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def class_b(db, event: EventType, course_b: CourseType) -> ClassType:
    id = db.add_class(
        event_id=event.id,
        name="Bahn B - Mittel",
        short_name="Bahn B - Mittel",
        course_id=course_b.id,
        params=ClassParams(),
    )
    item = db.get_class(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def entry_1(db, event: EventType, class_a: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event.id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_a.id,
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
    item = db.get_entry(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def entry_2(db, event: EventType, class_b: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event.id,
        competitor_id=None,
        first_name="Claudia",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_b.id,
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
    item = db.get_entry(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def entry_3(db, event: EventType, class_b: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event.id,
        competitor_id=None,
        first_name="Birgit",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_b.id,
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
    item = db.get_entry(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def entry_4(db, event: EventType, class_a: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event.id,
        competitor_id=None,
        first_name="Birgit",
        last_name="Derkel",
        gender="",
        year=None,
        class_id=class_a.id,
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
    item = db.get_entry(id=id)
    return copy.deepcopy(item)


def test_event_class_results(
    db,
    event: EventType,
    class_a: ClassType,
    class_b: ClassType,
    course_a: CourseType,
    course_b: CourseType,
    entry_1: EntryType,
    entry_2: EntryType,
    entry_3: EntryType,
    entry_4: EntryType,
):
    m_event, m_class_results = model.event_class_results(event_id=event.id)

    class_info_a = ClassInfoType(
        id=class_a.id,
        name=class_a.name,
        short_name=class_a.short_name,
        course_id=course_a.id,
        course_name=course_a.name,
        course_length=course_a.length,
        course_climb=course_a.climb,
        number_of_controls=len(course_a.controls),
        params=class_a.params,
    )
    class_info_b = ClassInfoType(
        id=class_b.id,
        name=class_b.name,
        short_name=class_b.short_name,
        course_id=course_b.id,
        course_name=course_b.name,
        course_length=course_b.length,
        course_climb=course_b.climb,
        number_of_controls=len(course_b.controls),
        params=class_b.params,
    )

    assert m_event == event
    assert m_class_results == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_4,
                    rank=1,
                    time_behind=3333 - 3333,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=2,
                    time_behind=9876 - 3333,
                ),
            ],
        ),
        (
            class_info_b,
            [
                RankedEntryType(
                    entry=entry_2,
                    rank=1,
                    time_behind=2001 - 2001,
                ),
                RankedEntryType(
                    entry=entry_3,
                    rank=2,
                    time_behind=2113 - 2001,
                ),
            ],
        ),
    ]

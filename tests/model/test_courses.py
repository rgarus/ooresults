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
from datetime import timezone

import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.course_type import CourseType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.model import model


@pytest.fixture
def db() -> SqliteRepo:
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def event_id(db: SqliteRepo) -> int:
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=False,
        fields=[],
    )


@pytest.fixture
def course_1_id(db: SqliteRepo, event_id: int) -> int:
    return db.add_course(
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


@pytest.fixture
def class_1_id(db: SqliteRepo, event_id: int, course_1_id: int) -> int:
    return db.add_class(
        event_id=event_id,
        name="Elite Men",
        short_name="E Men",
        course_id=course_1_id,
        params=ClassParams(),
    )


@pytest.fixture
def class_2_id(db: SqliteRepo, event_id: int) -> int:
    return db.add_class(
        event_id=event_id,
        name="Elite Women",
        short_name="E Women",
        course_id=None,
        params=ClassParams(),
    )


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
C1 = datetime.datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
C2 = datetime.datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
C3 = datetime.datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
F1 = datetime.datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)


@pytest.fixture
def entry_1(db: SqliteRepo, event_id: int, class_1_id: int) -> EntryType:
    id = db.add_entry(
        event_id=event_id,
        competitor_id=None,
        first_name="Claudia",
        last_name="Merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        club_id=None,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
    )
    result = PersonRaceResult(
        punched_start_time=S1,
        punched_finish_time=F1,
        status=ResultStatus.INACTIVE,
        time=None,
        split_times=[
            SplitTime(control_code="101", punch_time=C1, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="102", punch_time=C2, status=SpStatus.ADDITIONAL),
            SplitTime(control_code="103", punch_time=C3, status=SpStatus.ADDITIONAL),
        ],
    )
    result.compute_result(controls=["101", "102", "103"], class_params=ClassParams())
    db.update_entry_result(
        id=id,
        chip="7411",
        start_time=None,
        result=result,
    )
    item = db.get_entry(id=id)
    return copy.deepcopy(item)


def test_import_course_data_with_climb_update_existing_course(
    event_id: int, course_1_id: int
):
    courses = [
        {
            "name": "Bahn A",
            "length": 4800,
            "climb": 120,
            "controls": ["101", "102"],
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=[])

    co = model.get_courses(event_id=event_id)
    assert len(co) == 1
    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4800,
        climb=120,
        controls=["101", "102"],
    )


def test_import_course_data_without_climb_update_existing_course(
    event_id: int, course_1_id: int
):
    courses = [
        {
            "name": "Bahn A",
            "length": None,
            "climb": None,
            "controls": ["101", "102"],
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=[])

    co = model.get_courses(event_id=event_id)
    assert len(co) == 1
    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=None,
        climb=None,
        controls=["101", "102"],
    )


def test_import_course_data_add_not_existing_course(event_id: int, course_1_id: int):
    courses = [
        {
            "name": "Bahn B",
            "length": 4800,
            "climb": 120,
            "controls": ["104"],
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=[])

    co = model.get_courses(event_id=event_id)
    assert len(co) == 2
    assert co[1].id != co[0].id

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    assert co[1] == CourseType(
        id=co[1].id,
        event_id=event_id,
        name="Bahn B",
        length=4800,
        climb=120,
        controls=["104"],
    )


def test_import_course_data_update_or_add_courses(event_id: int, course_1_id: int):
    courses = [
        {
            "name": "Bahn A",
            "length": 4800,
            "climb": None,
            "controls": ["101", "102"],
        },
        {
            "name": "Bahn B",
            "length": 3900,
            "climb": 120,
            "controls": ["201", "102"],
        },
        {
            "name": "Bahn C",
            "length": None,
            "climb": None,
            "controls": [],
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=[])

    co = model.get_courses(event_id=event_id)
    assert len(co) == 3
    assert co[0].id != co[1].id
    assert co[0].id != co[2].id
    assert co[1].id != co[2].id

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4800,
        climb=None,
        controls=["101", "102"],
    )
    assert co[1] == CourseType(
        id=co[1].id,
        event_id=event_id,
        name="Bahn B",
        length=3900,
        climb=120,
        controls=["201", "102"],
    )
    assert co[2] == CourseType(
        id=co[2].id,
        event_id=event_id,
        name="Bahn C",
        length=None,
        climb=None,
        controls=[],
    )


def test_import_course_data_add_not_existing_class(
    event_id: int, class_1_id: int, course_1_id: int
):
    class_course = [
        {
            "class_name": "Beginners",
            "course_name": None,
        }
    ]
    model.import_courses(event_id=event_id, courses=[], class_course=class_course)

    co = model.get_courses(event_id=event_id)
    assert len(co) == 1
    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )

    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 2
    assert cl[0].id != cl[1].id

    assert cl[0] == ClassInfoType(
        id=cl[0].id,
        name="Beginners",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )
    assert cl[1] == ClassInfoType(
        id=class_1_id,
        name="Elite Men",
        short_name="E Men",
        course_id=course_1_id,
        course_name="Bahn A",
        course_length=4500,
        course_climb=90,
        number_of_controls=3,
        params=ClassParams(),
    )


def test_import_course_data_update_class_course_assignment(
    event_id: int, class_1_id: int, class_2_id: int, course_1_id: int
):
    courses = [
        {
            "name": "Bahn B",
            "length": 3900,
            "climb": 120,
            "controls": ["201", "102"],
        },
    ]
    class_course = [
        {
            "class_name": "Elite Men",
            "course_name": "Bahn B",
        }
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=class_course)

    co = model.get_courses(event_id=event_id)
    assert len(co) == 2
    assert co[0].id != co[1].id

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    assert co[1] == CourseType(
        id=co[1].id,
        event_id=event_id,
        name="Bahn B",
        length=3900,
        climb=120,
        controls=["201", "102"],
    )

    cl = model.get_classes(event_id=event_id)
    assert len(cl) == 2

    assert cl[0] == ClassInfoType(
        id=class_1_id,
        name="Elite Men",
        short_name="E Men",
        course_id=co[1].id,
        course_name="Bahn B",
        course_length=3900,
        course_climb=120,
        number_of_controls=2,
        params=ClassParams(),
    )
    assert cl[1] == ClassInfoType(
        id=class_2_id,
        name="Elite Women",
        short_name="E Women",
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


def test_import_course_data_remove_class_course_assigment(
    event_id: int, class_1_id: int, course_1_id: int
):
    class_course = [
        {
            "class_name": "Elite Men",
            "course_name": None,
        }
    ]
    model.import_courses(event_id=event_id, courses=[], class_course=class_course)

    co = model.get_courses(event_id=event_id)
    assert len(co) == 1

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )

    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 1

    assert cl[0] == ClassInfoType(
        id=class_1_id,
        name="Elite Men",
        short_name="E Men",
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


def test_import_course_data_update_or_add_class_course_assigments(
    event_id: int, course_1_id: int, class_1_id: int, class_2_id: int
):
    courses = [
        {
            "name": "Bahn A",
            "length": 4800,
            "climb": 120,
            "controls": ["101", "102"],
        },
        {
            "name": "Bahn B",
            "length": None,
            "climb": None,
            "controls": ["104"],
        },
    ]
    class_course = [
        {
            "class_name": "Elite Men",
            "course_name": "Bahn B",
        },
        {
            "class_name": "Elite Women",
            "course_name": "Bahn A",
        },
        {
            "class_name": "Beginners",
            "course_name": None,
        },
        {
            "class_name": "Elite",
            "course_name": "Bahn B",
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=class_course)

    co = model.get_courses(event_id=event_id)
    assert len(co) == 2
    assert co[0].id != co[1].id

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Bahn A",
        length=4800,
        climb=120,
        controls=["101", "102"],
    )
    assert co[1] == CourseType(
        id=co[1].id,
        event_id=event_id,
        name="Bahn B",
        length=None,
        climb=None,
        controls=["104"],
    )

    cl = model.get_classes(event_id=event_id)
    assert len(cl) == 4
    assert cl[0].id not in (class_1_id, class_2_id, cl[2].id, cl[3].id)
    assert cl[1].id not in (class_1_id, class_2_id, cl[2].id, cl[3].id)

    assert cl[0] == ClassInfoType(
        id=cl[0].id,
        name="Beginners",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )
    assert cl[1] == ClassInfoType(
        id=cl[1].id,
        name="Elite",
        short_name=None,
        course_id=co[1].id,
        course_name="Bahn B",
        course_length=None,
        course_climb=None,
        number_of_controls=1,
        params=ClassParams(),
    )
    assert cl[2] == ClassInfoType(
        id=class_1_id,
        name="Elite Men",
        short_name="E Men",
        course_id=co[1].id,
        course_name="Bahn B",
        course_length=None,
        course_climb=None,
        number_of_controls=1,
        params=ClassParams(),
    )
    assert cl[3] == ClassInfoType(
        id=class_2_id,
        name="Elite Women",
        short_name="E Women",
        course_id=course_1_id,
        course_name="Bahn A",
        course_length=4800,
        course_climb=120,
        number_of_controls=2,
        params=ClassParams(),
    )


def test_update_course_data_recalculates_entry_result(
    event_id: int, class_1_id: int, course_1_id: int, entry_1: EntryType
):
    model.update_course(
        id=course_1_id,
        event_id=event_id,
        name="Course 3",
        length=3900,
        climb=150,
        controls=["101", "104"],
    )
    co = model.get_courses(event_id=event_id)
    assert len(co) == 1

    assert co[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 3",
        length=3900,
        climb=150,
        controls=["101", "104"],
    )

    e = model.get_entries(event_id=event_id)
    assert len(e) == 1

    assert e[0].result == PersonRaceResult(
        start_time=S1,
        punched_start_time=S1,
        finish_time=F1,
        punched_finish_time=F1,
        status=ResultStatus.MISSING_PUNCH,
        time=8,
        split_times=[
            SplitTime(
                control_code="101",
                punch_time=C1,
                status=SpStatus.OK,
                time=2,
            ),
            SplitTime(
                control_code="104",
                punch_time=None,
                status=SpStatus.MISSING,
                time=None,
            ),
            SplitTime(
                control_code="102",
                punch_time=C2,
                status=SpStatus.ADDITIONAL,
                time=4,
            ),
            SplitTime(
                control_code="103",
                punch_time=C3,
                status=SpStatus.ADDITIONAL,
                time=6,
            ),
        ],
    )

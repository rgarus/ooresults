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

import pytest

from ooresults.repo import repo
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.repo.course_type import CourseType


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def event_id(db):
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=True,
        fields=[],
    )


@pytest.fixture
def course_1_id(db, event_id):
    return db.add_course(
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


@pytest.fixture
def course_2_id(db, event_id):
    return db.add_course(
        event_id=event_id,
        name="Course 2",
        length=None,
        climb=None,
        controls=[],
    )


@pytest.fixture
def class_id(db, event_id, course_1_id):
    return db.add_class(
        event_id=event_id,
        name="Class 1",
        short_name=None,
        course_id=course_1_id,
        params=ClassParams(),
    )


def test_get_courses_after_adding_one_course(db, event_id, course_1_id):
    c = db.get_courses(event_id=event_id)
    assert len(c) == 1
    assert c[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


def test_get_courses_after_adding_two_courses(db, event_id, course_1_id, course_2_id):
    c = db.get_courses(event_id=event_id)
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    assert c[1] == CourseType(
        id=course_2_id,
        event_id=event_id,
        name="Course 2",
        length=None,
        climb=None,
        controls=[],
    )


def test_get_first_added_course(db, event_id, course_1_id, course_2_id):
    c = db.get_course(id=course_1_id)
    assert c == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


def test_get_last_added_course(db, event_id, course_1_id, course_2_id):
    c = db.get_course(id=course_2_id)
    assert c == CourseType(
        id=course_2_id,
        event_id=event_id,
        name="Course 2",
        length=None,
        climb=None,
        controls=[],
    )


def test_update_first_added_course(db, event_id, course_1_id, course_2_id):
    db.update_course(
        id=course_1_id, name="Course 3", length=3900, climb=150, controls=["101"]
    )
    c = db.get_courses(event_id=event_id)
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CourseType(
        id=course_2_id,
        event_id=event_id,
        name="Course 2",
        length=None,
        climb=None,
        controls=[],
    )
    assert c[1] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 3",
        length=3900,
        climb=150,
        controls=["101"],
    )


def test_update_last_added_course(db, event_id, course_1_id, course_2_id):
    db.update_course(
        id=course_2_id,
        name="Course 3",
        length=5100,
        climb=None,
        controls=["301", "302", "303"],
    )
    c = db.get_courses(event_id=event_id)
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    assert c[1] == CourseType(
        id=course_2_id,
        event_id=event_id,
        name="Course 3",
        length=5100,
        climb=None,
        controls=["301", "302", "303"],
    )


def test_delete_first_added_course(db, event_id, course_1_id, course_2_id):
    db.delete_course(id=course_1_id)
    c = db.get_courses(event_id=event_id)
    assert len(c) == 1
    assert c[0] == CourseType(
        id=course_2_id,
        event_id=event_id,
        name="Course 2",
        length=None,
        climb=None,
        controls=[],
    )


def test_delete_last_added_course(db, event_id, course_1_id, course_2_id):
    db.delete_course(id=course_2_id)
    c = db.get_courses(event_id=event_id)
    assert len(c) == 1
    assert c[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


def test_delete_courses_deletes_all_courses(db, event_id, course_1_id, course_2_id):
    db.delete_courses(event_id=event_id)
    c = db.get_courses(event_id=event_id)
    assert len(c) == 0


def test_add_existing_name_raises_exception(db, event_id, course_1_id):
    with pytest.raises(repo.ConstraintError, match="Course already exist"):
        db.add_course(
            event_id=event_id, name="Course 1", length=None, climb=None, controls=[]
        )


def test_change_to_existing_name_raises_exception(db, course_1_id, course_2_id):
    with pytest.raises(repo.ConstraintError, match="Course already exist"):
        db.update_course(
            id=course_1_id, name="Course 2", length=None, climb=None, controls=[]
        )


def test_update_with_unknown_id_raises_exception(db, course_1_id):
    with pytest.raises(KeyError):
        db.update_course(
            id=course_1_id + 1, name="Course 2", length=None, climb=None, controls=[]
        )


def test_add_course_with_unknown_event_id_raises_exception(db, event_id):
    with pytest.raises(repo.EventNotFoundError):
        db.add_course(
            event_id=event_id + 1, name="Course 1", length=None, climb=None, controls=[]
        )


def test_delete_course_with_unknown_id_do_not_change_anything(
    db, event_id, course_1_id
):
    db.delete_course(id=course_1_id + 1)
    c = db.get_courses(event_id=event_id)
    assert len(c) == 1
    assert c[0] == CourseType(
        id=course_1_id,
        event_id=event_id,
        name="Course 1",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


def test_delete_course_used_in_class_raises_exception(
    db, event_id, class_id, course_1_id
):
    with pytest.raises(repo.CourseUsedError):
        db.delete_course(id=course_1_id)


def test_delete_courses_used_in_class_raises_exception(
    db, event_id, class_id, course_1_id
):
    with pytest.raises(repo.CourseUsedError):
        db.delete_courses(event_id=event_id)

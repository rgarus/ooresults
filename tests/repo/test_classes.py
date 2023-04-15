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
from ooresults.repo.result_type import ResultStatus


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


@pytest.fixture
def event_1_id(db):
    return db.add_event(
        name="Event 1",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
    )


@pytest.fixture
def event_2_id(db):
    return db.add_event(
        name="Event 2",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
    )


@pytest.fixture
def course_1_id(db, event_1_id):
    return db.add_course(
        event_id=event_1_id,
        name="Course 1",
        length=None,
        climb=None,
        controls=[],
    )


@pytest.fixture
def course_2_id(db, event_1_id):
    return db.add_course(
        event_id=event_1_id,
        name="Course 2",
        length=2300,
        climb=90,
        controls=["101", "102"],
    )


@pytest.fixture
def class_1_id(db, event_1_id):
    return db.add_class(
        event_id=event_1_id,
        name="Class 1",
        short_name="C 1",
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_2_id(db, event_1_id, course_1_id):
    return db.add_class(
        event_id=event_1_id,
        name="Class 2",
        short_name=None,
        course_id=course_1_id,
        params=ClassParams(),
    )


@pytest.fixture
def class_3_id(db, event_2_id):
    return db.add_class(
        event_id=event_2_id,
        name="Class 3",
        short_name="C 3",
        course_id=None,
        params=ClassParams(),
    )


@pytest.fixture
def entry_id(db, event_1_id, class_1_id):
    return db.add_entry(
        event_id=event_1_id,
        competitor_id=None,
        first_name="A",
        last_name="B",
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


def test_get_classes_after_adding_one_class(db, event_1_id, class_1_id):
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 1
    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()


def test_get_classes_for_first_event(
    db, event_1_id, course_1_id, class_1_id, class_2_id, class_3_id
):
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()
    assert c[1].id == class_2_id
    assert c[1].name == "Class 2"
    assert c[1].short_name is None
    assert c[1].course_id == course_1_id
    assert c[1].course == "Course 1"
    assert c[1].course_length is None
    assert c[1].course_climb is None
    assert c[1].number_of_controls == 0
    assert c[1].params == ClassParams()


def test_get_classes_for_second_event(
    db, event_2_id, course_1_id, class_1_id, class_2_id, class_3_id
):
    c = list(db.get_classes(event_id=event_2_id))
    assert len(c) == 1

    assert c[0].id == class_3_id
    assert c[0].name == "Class 3"
    assert c[0].short_name == "C 3"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()


def test_get_first_added_class(db, class_1_id, class_2_id):
    c = list(db.get_class(id=class_1_id))
    assert len(c) == 1
    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].params == ClassParams()


def test_get_last_added_class(db, course_1_id, class_1_id, class_2_id):
    c = list(db.get_class(id=class_2_id))
    assert len(c) == 1
    assert c[0].id == class_2_id
    assert c[0].name == "Class 2"
    assert c[0].short_name is None
    assert c[0].course_id == course_1_id
    assert c[0].params == ClassParams()


def test_update_first_added_class(db, event_1_id, course_1_id, class_1_id, class_2_id):
    db.update_class(
        id=class_1_id,
        name="Class 3",
        short_name="C 3",
        course_id=course_1_id,
        params=ClassParams(),
    )
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == class_2_id
    assert c[0].name == "Class 2"
    assert c[0].short_name is None
    assert c[0].course_id == course_1_id
    assert c[0].course == "Course 1"
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls == 0
    assert c[0].params == ClassParams()
    assert c[1].id == class_1_id
    assert c[1].name == "Class 3"
    assert c[1].short_name == "C 3"
    assert c[1].course_id == course_1_id
    assert c[1].course == "Course 1"
    assert c[1].course_length is None
    assert c[1].course_climb is None
    assert c[1].number_of_controls == 0
    assert c[1].params == ClassParams()


def test_update_last_added_class(db, event_1_id, class_1_id, class_2_id):
    db.update_class(
        id=class_2_id,
        name="Class 3",
        short_name="C 3",
        course_id=None,
        params=ClassParams(),
    )
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()
    assert c[1].id == class_2_id
    assert c[1].name == "Class 3"
    assert c[1].short_name == "C 3"
    assert c[1].course_id is None
    assert c[1].course is None
    assert c[1].course_length is None
    assert c[1].course_climb is None
    assert c[1].number_of_controls is None
    assert c[1].params == ClassParams()


def test_delete_first_added_class(db, event_1_id, course_1_id, class_1_id, class_2_id):
    db.delete_class(id=class_1_id)
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 1
    assert c[0].id == class_2_id
    assert c[0].name == "Class 2"
    assert c[0].short_name is None
    assert c[0].course_id == course_1_id
    assert c[0].course == "Course 1"
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls == 0
    assert c[0].params == ClassParams()


def test_delete_last_added_class(db, event_1_id, class_1_id, class_2_id):
    db.delete_class(id=class_2_id)
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 1
    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()


def test_delete_classes_deletes_all_classes(db, event_1_id, class_1_id, class_2_id):
    db.delete_classes(event_id=event_1_id)
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 0


def test_add_existing_name_raises_exception(db, event_1_id, class_1_id):
    with pytest.raises(repo.ConstraintError, match="Class already exist"):
        db.add_class(
            event_id=event_1_id,
            name="Class 1",
            short_name="XXX",
            course_id=None,
            params=ClassParams(),
        )


def test_change_to_existing_name_raises_exception(db, class_1_id, class_2_id):
    with pytest.raises(repo.ConstraintError, match="Class already exist"):
        db.update_class(
            id=class_1_id,
            name="Class 2",
            short_name=None,
            course_id=None,
            params=ClassParams(),
        )


def test_update_with_unknown_id_raises_exception(db, class_1_id):
    with pytest.raises(KeyError):
        db.update_class(
            id=class_1_id + 1,
            name="Class 2",
            short_name="C 2",
            course_id=None,
            params=ClassParams(),
        )


def test_add_class_with_unknown_event_id_raises_exception(db, event_1_id):
    with pytest.raises(repo.EventNotFoundError):
        db.add_class(
            event_id=event_1_id + 1,
            name="Class 1",
            short_name="C 1",
            course_id=None,
            params=ClassParams(),
        )


def test_delete_class_with_unknown_id_do_not_change_anything(
    db, event_1_id, class_1_id
):
    db.delete_class(id=class_1_id + 1)
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 1
    assert c[0].id == class_1_id
    assert c[0].name == "Class 1"
    assert c[0].short_name == "C 1"
    assert c[0].course_id is None
    assert c[0].course is None
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls is None
    assert c[0].params == ClassParams()


def test_delete_class_used_in_entry_raises_exception(
    db, event_1_id, entry_id, class_1_id
):
    with pytest.raises(repo.ClassUsedError):
        db.delete_class(id=class_1_id)


def test_delete_classes_if_entry_exist_raises_exception(
    db, event_1_id, entry_id, class_1_id
):
    with pytest.raises(repo.ClassUsedError):
        db.delete_classes(event_id=event_1_id)


def test_get_course_data(
    db, event_1_id, course_1_id, course_2_id, class_1_id, class_2_id
):
    db.update_class(
        id=class_1_id,
        name="Class 3",
        short_name="C 3",
        course_id=course_2_id,
        params=ClassParams(),
    )
    c = list(db.get_classes(event_id=event_1_id))
    assert len(c) == 2
    assert c[0].id != c[1].id

    assert c[0].id == class_2_id
    assert c[0].name == "Class 2"
    assert c[0].short_name is None
    assert c[0].course_id == course_1_id
    assert c[0].course == "Course 1"
    assert c[0].course_length is None
    assert c[0].course_climb is None
    assert c[0].number_of_controls == 0
    assert c[0].params == ClassParams()
    assert c[1].id == class_1_id
    assert c[1].name == "Class 3"
    assert c[1].short_name == "C 3"
    assert c[1].course_id == course_2_id
    assert c[1].course == "Course 2"
    assert c[1].course_length == 2300
    assert c[1].course_climb == 90
    assert c[1].number_of_controls == 2
    assert c[1].params == ClassParams()

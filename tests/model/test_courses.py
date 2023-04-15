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

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.class_params import ClassParams
from ooresults.handler import model


@pytest.fixture
def db():
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def event_id(db):
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=False,
    )


@pytest.fixture
def course_1_id(db, event_id):
    return db.add_course(
        event_id=event_id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )


@pytest.fixture
def class_1_id(db, event_id, course_1_id):
    return db.add_class(
        event_id=event_id,
        name="Elite Men",
        short_name="E Men",
        course_id=course_1_id,
        params=ClassParams(),
    )


@pytest.fixture
def class_2_id(db, event_id):
    return db.add_class(
        event_id=event_id,
        name="Elite Women",
        short_name="E Women",
        course_id=None,
        params=ClassParams(),
    )


def test_import_course_data_with_climb_update_existing_course(
    db, event_id, course_1_id
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

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 1
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4800
    assert co[0].climb == 120
    assert co[0].controls == ["101", "102"]


def test_import_course_data_without_climb_update_existing_course(
    db, event_id, course_1_id
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

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 1
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length is None
    assert co[0].climb is None
    assert co[0].controls == ["101", "102"]


def test_import_course_data_add_not_existing_course(db, event_id, course_1_id):
    courses = [
        {
            "name": "Bahn B",
            "length": 4800,
            "climb": 120,
            "controls": ["104"],
        },
    ]
    model.import_courses(event_id=event_id, courses=courses, class_course=[])

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 2
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4500
    assert co[0].climb == 90
    assert co[0].controls == ["101", "102", "103"]
    assert co[1].id != co[0].id
    assert co[1].name == "Bahn B"
    assert co[1].length == 4800
    assert co[1].climb == 120
    assert co[1].controls == ["104"]


def test_import_course_data_update_or_add_courses(db, event_id, course_1_id):
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

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 3
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4800
    assert co[0].climb is None
    assert co[0].controls == ["101", "102"]
    assert co[1].id != co[0].id
    assert co[1].name == "Bahn B"
    assert co[1].length == 3900
    assert co[1].climb == 120
    assert co[1].controls == ["201", "102"]
    assert co[2].id != co[0].id
    assert co[2].name == "Bahn C"
    assert co[2].length is None
    assert co[2].climb is None
    assert co[2].controls == []


def test_import_course_data_add_not_existing_class(
    db, event_id, class_1_id, course_1_id
):
    class_course = [
        {
            "class_name": "Beginners",
            "course_name": None,
        }
    ]
    model.import_courses(event_id=event_id, courses=[], class_course=class_course)

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 1
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4500
    assert co[0].climb == 90
    assert co[0].controls == ["101", "102", "103"]
    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 2
    assert cl[0].id != cl[1].id
    assert cl[0].name == "Beginners"
    assert cl[0].short_name is None
    assert cl[0].course_id is None
    assert cl[0].course is None
    assert cl[0].course_length is None
    assert cl[0].course_climb is None
    assert cl[0].number_of_controls is None
    assert cl[0].params == ClassParams()
    assert cl[1].id == class_1_id
    assert cl[1].name == "Elite Men"
    assert cl[1].short_name == "E Men"
    assert cl[1].course_id == course_1_id
    assert cl[1].course == "Bahn A"
    assert cl[1].course_length == 4500
    assert cl[1].course_climb == 90
    assert cl[1].number_of_controls == 3
    assert cl[1].params == ClassParams()


def test_import_course_data_update_class_course_assignment(
    db, event_id, class_1_id, class_2_id, course_1_id
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

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 2
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4500
    assert co[0].climb == 90
    assert co[0].controls == ["101", "102", "103"]
    assert co[1].id != course_1_id
    assert co[1].name == "Bahn B"
    assert co[1].length == 3900
    assert co[1].climb == 120
    assert co[1].controls == ["201", "102"]
    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 2
    assert cl[0].id == class_1_id
    assert cl[0].name == "Elite Men"
    assert cl[0].short_name == "E Men"
    assert cl[0].course_id == co[1].id
    assert cl[0].course == "Bahn B"
    assert cl[0].course_length == 3900
    assert cl[0].course_climb == 120
    assert cl[0].number_of_controls == 2
    assert cl[0].params == ClassParams()
    assert cl[1].id == class_2_id
    assert cl[1].name == "Elite Women"
    assert cl[1].short_name == "E Women"
    assert cl[1].course_id is None
    assert cl[1].course is None
    assert cl[1].course_length is None
    assert cl[1].course_climb is None
    assert cl[1].number_of_controls is None
    assert cl[1].params == ClassParams()


def test_import_course_data_remove_class_course_assigment(
    db, event_id, class_1_id, course_1_id
):
    class_course = [
        {
            "class_name": "Elite Men",
            "course_name": None,
        }
    ]
    model.import_courses(event_id=event_id, courses=[], class_course=class_course)

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 1
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4500
    assert co[0].climb == 90
    assert co[0].controls == ["101", "102", "103"]
    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 1
    assert cl[0].id == class_1_id
    assert cl[0].name == "Elite Men"
    assert cl[0].short_name == "E Men"
    assert cl[0].course_id is None
    assert cl[0].course is None
    assert cl[0].course_length is None
    assert cl[0].course_climb is None
    assert cl[0].number_of_controls is None
    assert cl[0].params == ClassParams()


def test_import_course_data_update_or_add_class_course_assigments(
    db, event_id, course_1_id, class_1_id, class_2_id
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

    co = list(model.get_courses(event_id=event_id))
    assert len(co) == 2
    assert co[0].id == course_1_id
    assert co[0].name == "Bahn A"
    assert co[0].length == 4800
    assert co[0].climb == 120
    assert co[0].controls == ["101", "102"]
    assert co[1].id != co[0].id
    assert co[1].name == "Bahn B"
    assert co[1].length is None
    assert co[1].climb is None
    assert co[1].controls == ["104"]

    cl = list(model.get_classes(event_id=event_id))
    assert len(cl) == 4
    assert cl[0].id not in (cl[2], cl[3])
    assert cl[0].name == "Beginners"
    assert cl[0].course_id is None
    assert cl[0].course is None
    assert cl[0].course_length is None
    assert cl[0].course_climb is None
    assert cl[0].number_of_controls is None
    assert cl[0].params == ClassParams()
    assert cl[1].id not in (cl[2], cl[3])
    assert cl[1].name == "Elite"
    assert cl[1].short_name is None
    assert cl[1].course_id == co[1].id
    assert cl[1].course == "Bahn B"
    assert cl[1].course_length is None
    assert cl[1].course_climb is None
    assert cl[1].number_of_controls == 1
    assert cl[1].params == ClassParams()
    assert cl[2].id == class_1_id
    assert cl[2].name == "Elite Men"
    assert cl[2].short_name == "E Men"
    assert cl[2].course_id == co[1].id
    assert cl[2].course == "Bahn B"
    assert cl[2].course_length is None
    assert cl[2].course_climb is None
    assert cl[2].number_of_controls == 1
    assert cl[2].params == ClassParams()
    assert cl[3].id == class_2_id
    assert cl[3].name == "Elite Women"
    assert cl[3].short_name == "E Women"
    assert cl[3].course_id == course_1_id
    assert cl[3].course == "Bahn A"
    assert cl[3].course_length == 4800
    assert cl[3].course_climb == 120
    assert cl[3].number_of_controls == 2
    assert cl[3].params == ClassParams()

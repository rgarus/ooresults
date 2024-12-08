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
from decimal import Decimal

import pytest

from ooresults.model import model
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.series_type import PersonSeriesResult
from ooresults.otypes.series_type import Points
from ooresults.otypes.series_type import Settings
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db():
    model.db = SqliteRepo(db=":memory:")
    return model.db


@pytest.fixture
def settings(db):
    settings = Settings(
        name="Series 1",
        nr_of_best_results=4,
        mode="Proportional 1",
        maximum_points=500,
        decimal_places=3,
    )
    db.update_series_settings(settings=settings)
    item = db.get_series_settings()
    return copy.deepcopy(item)


@pytest.fixture
def event_1(db) -> EventType:
    id = db.add_event(
        name="Event 1",
        date=datetime.date(year=2015, month=1, day=1),
        key=None,
        publish=False,
        series="Lauf 1",
        fields=[],
    )
    item = db.get_event(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def event_2(db) -> EventType:
    id = db.add_event(
        name="Event 2",
        date=datetime.date(year=2015, month=1, day=1),
        key=None,
        publish=False,
        series="Lauf 2",
        fields=[],
    )
    item = db.get_event(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def course_a(db, event_1: EventType) -> CourseType:
    id = db.add_course(
        event_id=event_1.id,
        name="Bahn A",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    item = db.get_course(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def course_b(db, event_1: EventType) -> CourseType:
    id = db.add_course(
        event_id=event_1.id,
        name="Bahn B",
        length=4500,
        climb=90,
        controls=["101", "102", "103"],
    )
    item = db.get_course(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def class_a(db, event_1: EventType, course_a: CourseType) -> ClassType:
    id = db.add_class(
        event_id=event_1.id,
        name="Bahn A - Lang",
        short_name="Bahn A - Lang",
        course_id=course_a.id,
        params=ClassParams(),
    )
    item = db.get_class(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def class_b(db, event_1: EventType, course_b: CourseType) -> ClassType:
    id = db.add_class(
        event_id=event_1.id,
        name="Bahn B - Mittel",
        short_name="Bahn B - Mittel",
        course_id=course_b.id,
        params=ClassParams(),
    )
    item = db.get_class(id=id)
    return copy.deepcopy(item)


@pytest.fixture
def entry_1(db, event_1: EventType, class_a: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event_1.id,
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
def entry_2(db, event_1: EventType, class_b: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event_1.id,
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
def entry_3(db, event_1: EventType, class_b: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event_1.id,
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
def entry_4(db, event_1: EventType, class_a: ClassType) -> EntryType:
    id = db.add_entry(
        event_id=event_1.id,
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


def test_build_series_result(
    db,
    settings: Settings,
    event_1: EventType,
    event_2: EventType,
    class_a: ClassType,
    class_b: ClassType,
    course_a: CourseType,
    course_b: CourseType,
    entry_1: EntryType,
    entry_2: EntryType,
    entry_3: EntryType,
    entry_4: EntryType,
):
    m_settings, m_events, m_ranked_classes = model.build_series_result()

    assert m_settings == settings
    assert m_events == [event_1, event_2]
    assert m_ranked_classes == [
        (
            class_a.name,
            [
                PersonSeriesResult(
                    first_name="Birgit",
                    last_name="Derkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("500.000")),
                    },
                    total_points=Decimal("500.000"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("168.742")),
                    },
                    total_points=Decimal("168.742"),
                    rank=2,
                ),
            ],
        ),
        (
            class_b.name,
            [
                PersonSeriesResult(
                    first_name="Claudia",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("500.000")),
                    },
                    total_points=Decimal("500.000"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Birgit",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("473.497")),
                    },
                    total_points=Decimal("473.497"),
                    rank=2,
                ),
            ],
        ),
    ]

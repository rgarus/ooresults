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
from collections.abc import Iterator
from datetime import timezone

import pytest

from ooresults import model
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.result_type import SpStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo import repo
from ooresults.repo.sqlite_repo import SqliteRepo


@pytest.fixture
def db() -> Iterator[SqliteRepo]:
    model.db = SqliteRepo(db=":memory:")
    yield model.db
    model.db.close()


@pytest.fixture
def event_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_event(
            name="Event",
            date=datetime.date(year=2020, month=1, day=1),
            key=None,
            publish=False,
            series=None,
            fields=[],
        )


@pytest.fixture
def course_1_id(db: SqliteRepo, event_id: int) -> int:
    with db.transaction():
        return db.add_course(
            event_id=event_id,
            name="Bahn A",
            length=4500,
            climb=90,
            controls=["101", "102", "103"],
        )


@pytest.fixture
def course_2_id(db: SqliteRepo, event_id: int) -> int:
    with db.transaction():
        return db.add_course(
            event_id=event_id,
            name="Bahn B",
            length=4300,
            climb=70,
            controls=["101", "104", "103"],
        )


@pytest.fixture
def class_1_id(db: SqliteRepo, event_id: int, course_1_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_id,
            name="Elite",
            short_name="E",
            course_id=course_1_id,
            params=ClassParams(),
        )


@pytest.fixture
def class_2_id(db: SqliteRepo, event_id: int, course_1_id: int) -> int:
    with db.transaction():
        return db.add_class(
            event_id=event_id,
            name="Elite Woman",
            short_name="E Woman",
            course_id=course_1_id,
            params=ClassParams(),
        )


@pytest.fixture
def club_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_club(
            name="OL Bundestag",
        )


@pytest.fixture
def competitor_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=None,
            gender="F",
            year=1957,
            chip="1234567",
        )


S1 = datetime.datetime(2015, 1, 1, 12, 38, 59, tzinfo=timezone.utc)
C1 = datetime.datetime(2015, 1, 1, 12, 39, 1, tzinfo=timezone.utc)
C2 = datetime.datetime(2015, 1, 1, 12, 39, 3, tzinfo=timezone.utc)
C3 = datetime.datetime(2015, 1, 1, 12, 39, 5, tzinfo=timezone.utc)
F1 = datetime.datetime(2015, 1, 1, 12, 39, 7, tzinfo=timezone.utc)


@pytest.fixture
def entry_1(
    db: SqliteRepo, event_id: int, class_1_id: int, competitor_id: int
) -> EntryType:
    with db.transaction():
        id = db.add_entry(
            event_id=event_id,
            competitor_id=competitor_id,
            class_id=class_1_id,
            club_id=None,
            not_competing=False,
            chip="4711",
            fields={},
            result=PersonRaceResult(),
            start=PersonRaceStart(),
        )
        result = PersonRaceResult(
            punched_start_time=S1,
            punched_finish_time=F1,
            si_punched_start_time=S1,
            si_punched_finish_time=None,
            status=ResultStatus.INACTIVE,
            time=None,
            split_times=[
                SplitTime(
                    control_code="101",
                    punch_time=C1,
                    si_punch_time=None,
                    status=SpStatus.ADDITIONAL,
                ),
                SplitTime(
                    control_code="103",
                    punch_time=C3,
                    si_punch_time=C3,
                    status=SpStatus.ADDITIONAL,
                ),
            ],
        )
        result.compute_result(
            controls=["101", "102", "103"], class_params=ClassParams()
        )
        db.update_entry_result(
            id=id,
            chip="4711",
            result=result,
            start=PersonRaceStart(),
        )
        item = db.get_entry(id=id)
        return copy.deepcopy(item)


@pytest.fixture
def entry_2(db: SqliteRepo, event_id: int) -> EntryType:
    with db.transaction():
        result = PersonRaceResult(
            punched_start_time=S1,
            punched_finish_time=F1,
            si_punched_start_time=S1,
            si_punched_finish_time=F1,
            status=ResultStatus.INACTIVE,
            time=None,
            split_times=[
                SplitTime(
                    control_code="101",
                    punch_time=C1,
                    si_punch_time=C1,
                    status=SpStatus.ADDITIONAL,
                ),
                SplitTime(
                    control_code="102",
                    punch_time=C2,
                    si_punch_time=C2,
                    status=SpStatus.ADDITIONAL,
                ),
                SplitTime(
                    control_code="103",
                    punch_time=C3,
                    si_punch_time=C3,
                    status=SpStatus.ADDITIONAL,
                ),
            ],
        )
        result.compute_result(controls=[], class_params=ClassParams())
        id = db.add_entry_result(
            event_id=event_id,
            chip="4748495",
            result=result,
            start=PersonRaceStart(),
        )
        return db.get_entry(id=id)


def test_if_an_entry_is_added_and_the_event_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, class_1_id: int
) -> None:
    model.events.delete_event(id=event_id)
    with db.transaction():
        with pytest.raises(repo.EventNotFoundError):
            db.get_event(id=event_id)

    with pytest.raises(repo.EventNotFoundError):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=None,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_1_id,
            club_id=None,
            not_competing=False,
            chip="4711",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_updated_and_the_event_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, entry_1: EntryType
) -> None:
    assert entry_1.class_id is not None

    model.events.delete_event(id=event_id)
    with db.transaction():
        with pytest.raises(repo.EventNotFoundError):
            db.get_event(id=event_id)

    with pytest.raises(repo.EventNotFoundError):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=entry_1.class_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_added_and_the_competitor_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, competitor_id: int, class_1_id: int
) -> None:
    model.competitors.delete_competitor(id=competitor_id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_competitor(id=competitor_id)

    with pytest.raises(repo.ConstraintError, match="Competitor deleted"):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=11,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_updated_and_the_entry_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, entry_1: EntryType
) -> None:
    assert entry_1.class_id is not None

    model.entries.delete_entry(id=entry_1.id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_entry(id=entry_1.id)

    with pytest.raises(repo.ConstraintError, match="Entry deleted"):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=entry_1.class_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_added_and_the_class_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, class_2_id: int
) -> None:
    model.classes.delete_class(id=class_2_id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_class(id=class_2_id)

    with pytest.raises(repo.ConstraintError, match="Class deleted"):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=None,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_2_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_updated_and_the_class_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, entry_1: EntryType, class_2_id: int
) -> None:
    model.classes.delete_class(id=class_2_id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_class(id=class_2_id)

    with pytest.raises(repo.ConstraintError, match="Class deleted"):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_2_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_added_and_the_club_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, class_1_id: int, club_id: int
) -> None:
    model.clubs.delete_club(id=club_id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_club(id=club_id)

    with pytest.raises(repo.ConstraintError, match="Club deleted"):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=None,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_1_id,
            club_id=club_id,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_updated_and_the_club_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, entry_1: EntryType, club_id: int
) -> None:
    assert entry_1.class_id is not None

    model.clubs.delete_club(id=club_id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_club(id=club_id)

    with pytest.raises(repo.ConstraintError, match="Club deleted"):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=entry_1.class_id,
            club_id=club_id,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_added_and_the_result_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, class_2_id: int, entry_2: EntryType
) -> None:
    model.entries.delete_entry(id=entry_2.id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_entry(id=entry_2.id)

    with pytest.raises(repo.ConstraintError, match="Result deleted"):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=None,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_2_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=entry_2.id,
        )


def test_if_an_entry_is_updated_and_the_result_no_longer_exists_then_an_exception_is_raised(
    db: SqliteRepo, entry_1: EntryType, entry_2: EntryType
) -> None:
    assert entry_1.class_id is not None

    model.entries.delete_entry(id=entry_2.id)
    with db.transaction():
        with pytest.raises(KeyError):
            db.get_entry(id=entry_2.id)

    with db.transaction():
        print(len(db.get_entries(event_id=entry_1.event_id)))

    with pytest.raises(repo.ConstraintError, match="Result deleted"):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=entry_1.class_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=entry_2.id,
        )


def test_if_an_entry_is_added_and_the_name_is_changed_to_an_existing_name_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, competitor_id: int, class_1_id: int
) -> None:
    with db.transaction():
        db.add_competitor(
            first_name="Birgit",
            last_name="Merkel",
            club_id=None,
            gender="F",
            year=1957,
            chip="1234567",
        )

    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        model.entries.add_or_update_entry(
            id=None,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Birgit",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=class_1_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )


def test_if_an_entry_is_updated_and_the_name_is_changed_to_an_existing_name_then_an_exception_is_raised(
    db: SqliteRepo, event_id: int, entry_1: EntryType
) -> None:
    assert entry_1.class_id is not None

    with db.transaction():
        db.add_competitor(
            first_name="Birgit",
            last_name="Merkel",
            club_id=None,
            gender="F",
            year=1957,
            chip="1234567",
        )

    with pytest.raises(repo.ConstraintError, match="Competitor already exist"):
        model.entries.add_or_update_entry(
            id=entry_1.id,
            event_id=entry_1.event_id,
            competitor_id=entry_1.competitor_id,
            first_name="Birgit",
            last_name="Merkel",
            gender="F",
            year=None,
            class_id=entry_1.class_id,
            club_id=None,
            not_competing=False,
            chip="4748495",
            fields={},
            status=ResultStatus.INACTIVE,
            start_time=None,
            result_id=None,
        )

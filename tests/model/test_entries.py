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
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.result_type import PersonRaceResult
from ooresults.otypes.result_type import ResultStatus
from ooresults.otypes.result_type import SplitTime
from ooresults.otypes.result_type import SpStatus
from ooresults.otypes.start_type import PersonRaceStart
from ooresults.repo.sqlite_repo import SqliteRepo


def t(a: datetime.datetime, b: datetime.datetime) -> int:
    diff = b.replace(microsecond=0) - a.replace(microsecond=0)
    return int(diff.total_seconds())


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
def club_id(db: SqliteRepo) -> int:
    with db.transaction():
        return db.add_club(
            name="OL Bundestag",
        )


@pytest.fixture
def competitor_id(db: SqliteRepo, club_id: int) -> int:
    with db.transaction():
        return db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=club_id,
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
    db: SqliteRepo, event_id: int, class_1_id: int, club_id: int, competitor_id: int
) -> EntryType:
    with db.transaction():
        id = db.add_entry(
            event_id=event_id,
            competitor_id=competitor_id,
            class_id=class_1_id,
            club_id=club_id,
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


def test_if_competitor_does_not_exist_a_new_competitor_is_added(
    db: SqliteRepo, event_id: int, class_1_id: int, club_id: int
) -> None:
    id, nc_changed = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=None,
        not_competing=False,
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )
    assert nc_changed is False

    with db.transaction():
        competitors = db.get_competitors()
    assert competitors == [
        CompetitorType(
            id=competitors[0].id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            chip="4748495",
            club_id=None,
            club_name=None,
        ),
    ]

    with db.transaction():
        data = db.get_entries(event_id=event_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=id,
        event_id=event_id,
        competitor_id=competitors[0].id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        class_name="Elite",
        not_competing=False,
        chip="4748495",
        fields={},
        result=PersonRaceResult(
            split_times=[
                SplitTime(control_code="101", status=SpStatus.MISSING),
                SplitTime(control_code="102", status=SpStatus.MISSING),
                SplitTime(control_code="103", status=SpStatus.MISSING),
            ],
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )


def test_add_existing_competitor_but_do_not_update_competitors_chip_and_club_if_already_defined(
    db: SqliteRepo, event_id: int, class_1_id: int, club_id: int
) -> None:
    with db.transaction():
        competitor_id = db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=club_id,
            gender="F",
            year=1957,
            chip="1234567",
        )

    id, _ = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=None,
        not_competing=False,
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )

    with db.transaction():
        data = db.get_entries(event_id=event_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=id,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        class_name="Elite",
        not_competing=False,
        chip="4748495",
        fields={},
        result=PersonRaceResult(
            split_times=[
                SplitTime(control_code="101", status=SpStatus.MISSING),
                SplitTime(control_code="102", status=SpStatus.MISSING),
                SplitTime(control_code="103", status=SpStatus.MISSING),
            ],
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    with db.transaction():
        data = db.get_competitor(id=competitor_id)
    assert data == CompetitorType(
        id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="1234567",
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_add_existing_competitor_and_update_competitors_chip_and_club_if_undefined(
    db: SqliteRepo, event_id: int, class_1_id: int, club_id: int
) -> None:
    with db.transaction():
        competitor_id = db.add_competitor(
            first_name="Angela",
            last_name="Merkel",
            club_id=None,
            gender="",
            year=None,
            chip="",
        )

    id, _ = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )

    with db.transaction():
        data = db.get_entries(event_id=event_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=id,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        class_name="Elite",
        not_competing=False,
        chip="4748495",
        fields={},
        result=PersonRaceResult(
            split_times=[
                SplitTime(control_code="101", status=SpStatus.MISSING),
                SplitTime(control_code="102", status=SpStatus.MISSING),
                SplitTime(control_code="103", status=SpStatus.MISSING),
            ],
        ),
        start=PersonRaceStart(),
        club_id=club_id,
        club_name="OL Bundestag",
    )

    with db.transaction():
        data = db.get_competitor(id=competitor_id)
    assert data == CompetitorType(
        id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        chip="4748495",
        club_id=club_id,
        club_name="OL Bundestag",
    )


def test_add_entry_without_result(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
) -> None:
    id, nc_changed = model.entries.add_or_update_entry(
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
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )
    assert nc_changed is False

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_if_updating_an_entry_then_the_key_data_of_the_competitor_are_also_updated(
    db: SqliteRepo,
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_1: EntryType,
) -> None:
    assert competitor_id == entry_1.competitor_id

    model.entries.add_or_update_entry(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="angela",
        last_name="merkel",
        gender="",
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

    with db.transaction():
        competitors = db.get_competitors()
    assert competitors == [
        CompetitorType(
            id=competitor_id,
            first_name="angela",
            last_name="merkel",
            gender="",
            year=None,
            chip="1234567",
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]

    with db.transaction():
        data = db.get_entries(event_id=event_id)
    assert len(data) == 1

    assert data[0] == EntryType(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="angela",
        last_name="merkel",
        gender="",
        year=None,
        class_id=class_1_id,
        class_name="Elite",
        not_competing=False,
        chip="4748495",
        fields={},
        result=entry_1.result,
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )


@pytest.mark.parametrize(
    "nc1_input, nc2_input",
    [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ],
)
def test_if_an_already_registered_competitor_is_added_then_not_competing_is_set_to_true(
    nc1_input: bool,
    nc2_input: bool,
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
) -> None:
    id1, nc_changed = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=None,
        not_competing=nc1_input,
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )
    assert nc_changed is False

    id2, nc_changed = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=None,
        class_id=class_1_id,
        club_id=None,
        not_competing=nc2_input,
        chip="4748495",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )
    assert nc_changed is (not nc2_input)

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=id1,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=nc1_input,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
        EntryType(
            id=id2,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=True,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_add_entry_with_result(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_2: EntryType,
) -> None:
    id, nc_changed = model.entries.add_or_update_entry(
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
        result_id=entry_2.id,
    )
    assert nc_changed is False

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                start_time=S1,
                finish_time=F1,
                punched_start_time=S1,
                punched_finish_time=F1,
                si_punched_start_time=S1,
                si_punched_finish_time=F1,
                status=ResultStatus.OK,
                time=t(S1, F1),
                split_times=[
                    SplitTime(
                        control_code="101",
                        punch_time=C1,
                        si_punch_time=C1,
                        time=t(S1, C1),
                        status=SpStatus.OK,
                    ),
                    SplitTime(
                        control_code="102",
                        punch_time=C2,
                        si_punch_time=C2,
                        time=t(S1, C2),
                        status=SpStatus.OK,
                    ),
                    SplitTime(
                        control_code="103",
                        punch_time=C3,
                        si_punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.OK,
                    ),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_update_entry_remove_result_and_store_removed_result_without_edits(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_1: EntryType,
) -> None:
    id, _ = model.entries.add_or_update_entry(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4711",
        fields={},
        status=ResultStatus.MISSING_PUNCH,
        start_time=None,
        result_id=-1,
    )

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=None,
            first_name=None,
            last_name=None,
            chip="4711",
            result=PersonRaceResult(
                start_time=S1,
                finish_time=None,
                punched_start_time=S1,
                punched_finish_time=None,
                si_punched_start_time=S1,
                si_punched_finish_time=None,
                status=ResultStatus.FINISHED,
                time=None,
                split_times=[
                    SplitTime(
                        control_code="103",
                        si_punch_time=C3,
                        punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.ADDITIONAL,
                    ),
                ],
            ),
        ),
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4711",
            fields={},
            result=PersonRaceResult(
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_update_entry_remove_result_with_status_disqualified_do_not_change_status(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_1: EntryType,
) -> None:
    id, _ = model.entries.add_or_update_entry(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4711",
        fields={},
        status=ResultStatus.DISQUALIFIED,
        start_time=None,
        result_id=-1,
    )

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=None,
            first_name=None,
            last_name=None,
            chip="4711",
            result=PersonRaceResult(
                start_time=S1,
                finish_time=None,
                punched_start_time=S1,
                punched_finish_time=None,
                si_punched_start_time=S1,
                si_punched_finish_time=None,
                status=ResultStatus.FINISHED,
                time=None,
                split_times=[
                    SplitTime(
                        control_code="103",
                        si_punch_time=C3,
                        punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.ADDITIONAL,
                    ),
                ],
            ),
        ),
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4711",
            fields={},
            result=PersonRaceResult(
                status=ResultStatus.DISQUALIFIED,
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_update_entry_change_status_and_remove_result_stores_changed_status(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_1: EntryType,
) -> None:
    id, _ = model.entries.add_or_update_entry(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4711",
        fields={},
        status=ResultStatus.DID_NOT_FINISH,
        start_time=None,
        result_id=-1,
    )

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=None,
            first_name=None,
            last_name=None,
            chip="4711",
            result=PersonRaceResult(
                start_time=S1,
                finish_time=None,
                punched_start_time=S1,
                punched_finish_time=None,
                si_punched_start_time=S1,
                si_punched_finish_time=None,
                status=ResultStatus.FINISHED,
                time=None,
                split_times=[
                    SplitTime(
                        control_code="103",
                        si_punch_time=C3,
                        punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.ADDITIONAL,
                    ),
                ],
            ),
        ),
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4711",
            fields={},
            result=PersonRaceResult(
                status=ResultStatus.DID_NOT_FINISH,
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_update_entry_replace_result_and_store_replaced_result_without_edits(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
    entry_1: EntryType,
    entry_2: EntryType,
) -> None:
    id, _ = model.entries.add_or_update_entry(
        id=entry_1.id,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="4711",
        fields={},
        status=ResultStatus.OK,
        start_time=None,
        result_id=entry_2.id,
    )

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=entries[0].id,
            event_id=event_id,
            competitor_id=None,
            first_name=None,
            last_name=None,
            chip="4711",
            result=PersonRaceResult(
                start_time=S1,
                finish_time=None,
                punched_start_time=S1,
                punched_finish_time=None,
                si_punched_start_time=S1,
                si_punched_finish_time=None,
                status=ResultStatus.FINISHED,
                time=None,
                split_times=[
                    SplitTime(
                        control_code="103",
                        si_punch_time=C3,
                        punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.ADDITIONAL,
                    ),
                ],
            ),
        ),
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="4748495",
            fields={},
            result=PersonRaceResult(
                start_time=S1,
                finish_time=F1,
                punched_start_time=S1,
                punched_finish_time=F1,
                si_punched_start_time=S1,
                si_punched_finish_time=F1,
                status=ResultStatus.OK,
                time=t(S1, F1),
                split_times=[
                    SplitTime(
                        control_code="101",
                        punch_time=C1,
                        si_punch_time=C1,
                        time=t(S1, C1),
                        status=SpStatus.OK,
                    ),
                    SplitTime(
                        control_code="102",
                        punch_time=C2,
                        si_punch_time=C2,
                        time=t(S1, C2),
                        status=SpStatus.OK,
                    ),
                    SplitTime(
                        control_code="103",
                        punch_time=C3,
                        si_punch_time=C3,
                        time=t(S1, C3),
                        status=SpStatus.OK,
                    ),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]


def test_update_entry_set_status_to_dns(
    event_id: int,
    class_1_id: int,
    club_id: int,
    competitor_id: int,
) -> None:
    id, _ = model.entries.add_or_update_entry(
        id=None,
        event_id=event_id,
        competitor_id=None,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.INACTIVE,
        start_time=None,
        result_id=None,
    )
    model.entries.add_or_update_entry(
        id=id,
        event_id=event_id,
        competitor_id=competitor_id,
        first_name="Angela",
        last_name="Merkel",
        gender="F",
        year=1957,
        class_id=class_1_id,
        club_id=club_id,
        not_competing=False,
        chip="",
        fields={},
        status=ResultStatus.DID_NOT_START,
        start_time=None,
        result_id=None,
    )

    entries = model.entries.get_entries(event_id=event_id)
    assert entries == [
        EntryType(
            id=id,
            event_id=event_id,
            competitor_id=competitor_id,
            first_name="Angela",
            last_name="Merkel",
            gender="F",
            year=1957,
            class_id=class_1_id,
            class_name="Elite",
            not_competing=False,
            chip="",
            fields={},
            result=PersonRaceResult(
                start_time=None,
                finish_time=None,
                punched_start_time=None,
                punched_finish_time=None,
                si_punched_start_time=None,
                si_punched_finish_time=None,
                status=ResultStatus.DID_NOT_START,
                time=None,
                split_times=[
                    SplitTime(control_code="101", status=SpStatus.MISSING),
                    SplitTime(control_code="102", status=SpStatus.MISSING),
                    SplitTime(control_code="103", status=SpStatus.MISSING),
                ],
            ),
            start=PersonRaceStart(),
            club_id=club_id,
            club_name="OL Bundestag",
        ),
    ]

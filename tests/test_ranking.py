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


from ooresults.model import build_results
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.start_type import PersonRaceStart
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.class_params import ClassParams


def test_ranking_with_one_class():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=9876,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH,
            time=1800,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.DID_NOT_START,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_2,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=2,
                    time_behind=9876 - 2001,
                ),
                RankedEntryType(
                    entry=entry_3,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_4,
                    rank=None,
                    time_behind=None,
                ),
            ],
        )
    ]


def test_ranking_with_two_classes():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    class_info_b = ClassInfoType(
        id=2,
        name="Bahn B - Mittel",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=9876,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=2,
        class_name="Bahn B - Mittel",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=2,
        class_name="Bahn B - Mittel",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2113,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=3333,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
            class_info_b,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_4,
                    rank=1,
                    time_behind=0,
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
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_3,
                    rank=2,
                    time_behind=2113 - 2001,
                ),
            ],
        ),
    ]


def test_ranking_with_two_winners():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH,
            time=9876,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_3,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_2,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=None,
                    time_behind=None,
                ),
            ],
        )
    ]


def test_ranking_entries_with_same_time_are_orderd_by_name():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_3,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_4,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_2,
                    rank=1,
                    time_behind=0,
                ),
            ],
        )
    ]


def test_ranking_entries_with_same_time_are_orderd_by_name_score():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(otype="score"),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2000,
            extensions={"score": 15.6},
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Tanja",
        last_name="Terkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
            extensions={"score": 15.6},
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2000,
            extensions={"score": 15.6},
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
            extensions={"score": 15.6},
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_3,
                    rank=1,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=1,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_4,
                    rank=3,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_2,
                    rank=3,
                    time_behind=None,
                ),
            ],
        )
    ]


def test_ranking_with_not_competing_runners():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=9876,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=True,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.OK,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=True,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH,
            time=1800,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.DID_NOT_START,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_1,
                    rank=1,
                    time_behind=0,
                ),
                RankedEntryType(
                    entry=entry_2,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_3,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_4,
                    rank=None,
                    time_behind=None,
                ),
            ],
        )
    ]


def test_ranking_with_started_and_finished_runners():
    class_info_a = ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )

    entry_1 = EntryType(
        id=1,
        event_id=1,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.INACTIVE,
            time=1800,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_2 = EntryType(
        id=2,
        event_id=1,
        competitor_id=4,
        first_name="Birgit",
        last_name="Derkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.ACTIVE,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_3 = EntryType(
        id=3,
        event_id=1,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.FINISHED,
            time=9876,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    entry_4 = EntryType(
        id=4,
        event_id=1,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        gender=None,
        year=None,
        class_id=1,
        class_name="Bahn A - Lang",
        not_competing=False,
        chip=None,
        fields={},
        result=PersonRaceResult(
            status=ResultStatus.FINISHED,
            time=2001,
        ),
        start=PersonRaceStart(),
        club_id=None,
        club_name=None,
    )

    data = build_results.build_results(
        class_infos=[
            class_info_a,
        ],
        entries=[
            entry_1,
            entry_2,
            entry_3,
            entry_4,
        ],
    )
    assert data == [
        (
            class_info_a,
            [
                RankedEntryType(
                    entry=entry_4,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_3,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_2,
                    rank=None,
                    time_behind=None,
                ),
                RankedEntryType(
                    entry=entry_1,
                    rank=None,
                    time_behind=None,
                ),
            ],
        )
    ]

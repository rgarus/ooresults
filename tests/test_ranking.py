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


from ooresults.handler import build_results
from ooresults.repo import result_type
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.class_params import ClassParams


class Class_:
    def __init__(self, name: str, params: ClassParams):
        self.name = name
        self.params = params


def test_ranking_with_one_class():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams())
    data = build_results.build_results(
        classes=[
            class_a,
        ],
        results=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=9876
                ),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Derkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.DID_NOT_START
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=9876
                    ),
                    "rank": 2,
                    "time_behind": 9876 - 2001,
                    "points": 2001 / 9876,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.MISSING_PUNCH, time=None
                    ),
                    "rank": None,
                    "points": 0,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Derkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.DID_NOT_START, time=None
                    ),
                    "rank": None,
                },
            ],
        )
    ]


def test_ranking_with_two_classes():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams())
    class_b = Class_(name="Bahn B - Mittel", params=ClassParams())
    data = build_results.build_results(
        classes=[
            class_a,
            class_b,
        ],
        results=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=9876
                ),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn B - Mittel",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn B - Mittel",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2113
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Derkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=3333
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Birgit",
                    "last_name": "Derkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=3333
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=9876
                    ),
                    "rank": 2,
                    "time_behind": 9876 - 3333,
                    "points": 3333 / 9876,
                },
            ],
        ),
        (
            class_b,
            [
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn B - Mittel",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Merkel",
                    "class_": "Bahn B - Mittel",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2113
                    ),
                    "rank": 2,
                    "time_behind": 2113 - 2001,
                    "points": 2001 / 2113,
                },
            ],
        ),
    ]


def test_ranking_with_two_winners():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams())
    data = build_results.build_results(
        classes=[
            class_a,
        ],
        results=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH, time=9876
                ),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Birgit",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.MISSING_PUNCH, time=9876
                    ),
                    "rank": None,
                    "points": 0,
                },
            ],
        )
    ]


def test_ranking_entries_with_same_time_are_orderd_by_name():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams())
    data = build_results.build_results(
        classes=[
            class_a,
        ],
        results=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Derkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Birgit",
                    "last_name": "Derkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 1.0,
                },
            ],
        )
    ]


def test_ranking_entries_with_same_time_are_orderd_by_name_2():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams(otype="score"))
    data = build_results.build_results(
        classes=[
            class_a,
        ],
        results=[
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2000, extensions={"score": 15.6}
                ),
            },
            {
                "first_name": "Tanja",
                "last_name": "Terkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001, extensions={"score": 15.6}
                ),
            },
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2000, extensions={"score": 15.6}
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Derkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001, extensions={"score": 15.6}
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2000, extensions={"score": 15.6}
                    ),
                    "rank": 1,
                },
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2000, extensions={"score": 15.6}
                    ),
                    "rank": 1,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Derkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001, extensions={"score": 15.6}
                    ),
                    "rank": 3,
                },
                {
                    "first_name": "Tanja",
                    "last_name": "Terkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001, extensions={"score": 15.6}
                    ),
                    "rank": 3,
                },
            ],
        )
    ]


def test_ranking_with_not_competing_runners():
    class_a = Class_(name="Bahn A - Lang", params=ClassParams())
    data = build_results.build_results(
        classes=[
            class_a,
        ],
        results=[
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=9876
                ),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": True,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.OK, time=2001
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "gender": "",
                "year": "",
                "not_competing": True,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.MISSING_PUNCH
                ),
            },
            {
                "first_name": "Birgit",
                "last_name": "Derkel",
                "gender": "",
                "year": "",
                "not_competing": False,
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(
                    status=ResultStatus.DID_NOT_START
                ),
            },
        ],
    )
    assert data == [
        (
            class_a,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=9876
                    ),
                    "rank": 1,
                    "time_behind": 0,
                    "points": 2001 / 2001,
                },
                {
                    "first_name": "Claudia",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": True,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.OK, time=2001
                    ),
                    "rank": None,
                    "points": 0,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Merkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": True,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.MISSING_PUNCH, time=None
                    ),
                    "rank": None,
                    "points": 0,
                },
                {
                    "first_name": "Birgit",
                    "last_name": "Derkel",
                    "class_": "Bahn A - Lang",
                    "gender": "",
                    "year": "",
                    "not_competing": False,
                    "result": result_type.PersonRaceResult(
                        status=ResultStatus.DID_NOT_START, time=None
                    ),
                    "rank": None,
                },
            ],
        )
    ]

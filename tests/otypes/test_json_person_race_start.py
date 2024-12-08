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


from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict

from pytest import fixture

from ooresults.otypes.start_type import PersonRaceStart


@fixture
def c_min() -> PersonRaceStart:
    return PersonRaceStart()


@fixture
def d_min() -> Dict:
    return {}


@fixture
def j_min() -> str:
    return "{}"


def test_min_to_dict(c_min: PersonRaceStart, d_min: Dict):
    assert c_min.to_dict() == d_min


def test_min_to_json(c_min: PersonRaceStart, j_min: str):
    assert c_min.to_json() == j_min


def test_min_from_dict(d_min: Dict, c_min: PersonRaceStart):
    assert PersonRaceStart.from_dict(d_min) == c_min


def test_min_from_json(j_min: str, c_min: PersonRaceStart):
    assert PersonRaceStart.from_json(j_min) == c_min


@fixture
def c_max() -> PersonRaceStart:
    return PersonRaceStart(
        start_time=datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    )


@fixture
def d_max() -> Dict:
    return {"startTime": "2020-02-09T10:00:00+01:00"}


@fixture
def j_max() -> str:
    return '{"startTime":"2020-02-09T10:00:00+01:00"}'


def test_max_to_dict(c_max: PersonRaceStart, d_max: Dict):
    assert c_max.to_dict() == d_max


def test_max_to_json(c_max: PersonRaceStart, j_max: str):
    assert c_max.to_json() == j_max


def test_max_from_dict(d_max: Dict, c_max: PersonRaceStart):
    assert PersonRaceStart.from_dict(d_max) == c_max


def test_max_from_json(j_max: str, c_max: PersonRaceStart):
    assert PersonRaceStart.from_json(j_max) == c_max

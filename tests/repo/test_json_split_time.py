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

from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus


@fixture
def c_min() -> SplitTime:
    return SplitTime(control_code="144")


@fixture
def d_min() -> Dict:
    return {
        "controlCode": "144",
        "legVoided": False,
    }


@fixture
def j_min() -> str:
    return "{" '"controlCode":"144",' '"legVoided":false' "}"


def test_min_to_dict(c_min: SplitTime, d_min: Dict):
    assert c_min.to_dict() == d_min


def test_min_to_json(c_min: SplitTime, j_min: str):
    assert c_min.to_json() == j_min


def test_min_from_dict(d_min: Dict, c_min: SplitTime):
    assert SplitTime.from_dict(d_min) == c_min


def test_min_from_json(j_min: str, c_min: SplitTime):
    assert SplitTime.from_json(j_min) == c_min


@fixture
def c_max() -> SplitTime:
    return SplitTime(
        control_code="257",
        punch_time=SplitTime.NO_TIME,
        si_punch_time=datetime(
            2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))
        ),
        time=34,
        status=SpStatus.ADDITIONAL,
        leg_voided=True,
    )


@fixture
def d_max() -> Dict:
    return {
        "controlCode": "257",
        "punchTime": "1970-01-01T00:00:00+00:00",
        "siPunchTime": "2020-02-09T10:00:00+01:00",
        "time": 34,
        "status": 2,
        "legVoided": True,
    }


@fixture
def j_max() -> str:
    return (
        "{"
        '"controlCode":"257",'
        '"punchTime":"1970-01-01T00:00:00+00:00",'
        '"siPunchTime":"2020-02-09T10:00:00+01:00",'
        '"time":34,'
        '"status":2,'
        '"legVoided":true'
        "}"
    )


def test_max_to_dict(c_max: SplitTime, d_max: Dict):
    assert c_max.to_dict() == d_max


def test_max_to_json(c_max: SplitTime, j_max: str):
    assert c_max.to_json() == j_max


def test_max_from_dict(d_max: Dict, c_max: SplitTime):
    assert SplitTime.from_dict(d_max) == c_max


def test_max_from_json(j_max: str, c_max: SplitTime):
    assert SplitTime.from_json(j_max) == c_max

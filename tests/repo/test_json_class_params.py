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

from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_params import VoidedLeg


@fixture
def c_min() -> ClassParams:
    return ClassParams()


@fixture
def d_min() -> Dict:
    return {
        "otype": "standard",
        "usingStartControl": "if_punched",
        "applyHandicapRule": False,
        "voidedLegs": [],
    }


@fixture
def j_min() -> str:
    return (
        "{"
        '"otype":"standard",'
        '"usingStartControl":"if_punched",'
        '"applyHandicapRule":false,'
        '"voidedLegs":[]'
        "}"
    )


def test_min_to_dict(c_min: ClassParams, d_min: Dict):
    assert c_min.to_dict() == d_min


def test_min_to_json(c_min: ClassParams, j_min: str):
    assert c_min.to_json() == j_min


def test_min_from_dict(d_min: Dict, c_min: ClassParams):
    assert ClassParams.from_dict(d_min) == c_min


def test_min_from_json(j_min: str, c_min: ClassParams):
    assert ClassParams.from_json(j_min) == c_min


@fixture
def c_max() -> ClassParams:
    return ClassParams(
        otype="score",
        using_start_control="yes",
        mass_start=datetime(2020, 2, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=1))),
        time_limit=50,
        penalty_controls=120,
        penalty_overtime=15,
        apply_handicap_rule=True,
        voided_legs=[
            VoidedLeg(control_1="100", control_2="100"),
            VoidedLeg(control_1="120", control_2="124"),
            VoidedLeg(control_1="133", control_2="121"),
        ],
    )


@fixture
def d_max() -> Dict:
    return {
        "otype": "score",
        "usingStartControl": "yes",
        "massStart": "2020-02-09T10:00:00+01:00",
        "timeLimit": 50,
        "penaltyControls": 120,
        "penaltyOvertime": 15,
        "applyHandicapRule": True,
        "voidedLegs": [
            {"control1": "100", "control2": "100"},
            {"control1": "120", "control2": "124"},
            {"control1": "133", "control2": "121"},
        ],
    }


@fixture
def j_max() -> str:
    return (
        "{"
        '"otype":"score",'
        '"usingStartControl":"yes",'
        '"massStart":"2020-02-09T10:00:00+01:00",'
        '"timeLimit":50,'
        '"penaltyControls":120,'
        '"penaltyOvertime":15,'
        '"applyHandicapRule":true,'
        '"voidedLegs":['
        '{"control1":"100","control2":"100"},'
        '{"control1":"120","control2":"124"},'
        '{"control1":"133","control2":"121"}]'
        "}"
    )


def test_max_to_dict(c_max: ClassParams, d_max: Dict):
    assert c_max.to_dict() == d_max


def test_max_to_json(c_max: ClassParams, j_max: str):
    assert c_max.to_json() == j_max


def test_max_from_dict(d_max: Dict, c_max: ClassParams):
    assert ClassParams.from_dict(d_max) == c_max


def test_max_from_json(j_max: str, c_max: ClassParams):
    assert ClassParams.from_json(j_max) == c_max

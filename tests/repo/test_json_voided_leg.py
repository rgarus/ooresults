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


from typing import Dict

from pytest import fixture

from ooresults.repo.class_params import VoidedLeg


@fixture
def c_max() -> VoidedLeg:
    return VoidedLeg(
        control_1="257",
        control_2="147",
    )


@fixture
def d_max() -> Dict:
    return {
        "control1": "257",
        "control2": "147",
    }


@fixture
def j_max() -> str:
    return '{"control1":"257","control2":"147"}'


def test_max_to_dict(c_max: VoidedLeg, d_max: Dict):
    assert c_max.to_dict() == d_max


def test_max_to_json(c_max: VoidedLeg, j_max: str):
    assert c_max.to_json() == j_max


def test_max_from_dict(d_max: Dict, c_max: VoidedLeg):
    assert VoidedLeg.from_dict(d_max) == c_max


def test_max_from_json(j_max: str, c_max: VoidedLeg):
    assert VoidedLeg.from_json(j_max) == c_max

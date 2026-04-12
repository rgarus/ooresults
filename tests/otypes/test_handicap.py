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


from ooresults.otypes.handicap import Handicap


def test_female_without_year():
    assert Handicap.factor(female=True, age=None) == 0.8716


def test_female_less_min_year():
    assert Handicap.factor(female=True, age=1) == 0.7626


def test_female_greater_max_year():
    assert Handicap.factor(female=True, age=99) == 0.3191


def test_female_with_year():
    assert Handicap.factor(female=True, age=44) == 0.8154


def test_male_without_year():
    assert Handicap.factor(female=False, age=None) == 1.0000


def test_male_less_min_year():
    assert Handicap.factor(female=False, age=1) == 0.7886


def test_male_greater_max_year():
    assert Handicap.factor(female=False, age=99) == 0.4321


def test_male_with_year():
    assert Handicap.factor(female=False, age=44) == 0.9169

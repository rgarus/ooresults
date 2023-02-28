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


from ooresults.handler import handicap


def test_female_without_year():
    h = handicap.Handicap()
    assert h.factor(female=True, year=None) == 0.8716


def test_female_less_min_year():
    h = handicap.Handicap()
    assert h.factor(female=True, year=1) == 0.7626


def test_female_greater_max_year():
    h = handicap.Handicap()
    assert h.factor(female=True, year=99) == 0.3191


def test_female_with_year():
    h = handicap.Handicap()
    assert h.factor(female=True, year=44) == 0.8154


def test_male_without_year():
    h = handicap.Handicap()
    assert h.factor(female=False, year=None) == 1.0000


def test_male_less_min_year():
    h = handicap.Handicap()
    assert h.factor(female=False, year=1) == 0.7886


def test_male_greater_max_year():
    h = handicap.Handicap()
    assert h.factor(female=False, year=99) == 0.4321


def test_male_with_year():
    h = handicap.Handicap()
    assert h.factor(female=False, year=44) == 0.9169

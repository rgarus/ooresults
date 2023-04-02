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


from ooresults.utils import globals


def test_minutes_seconds_of_none():
    assert globals.minutes_seconds(time=None) == ""


def test_minutes_seconds_of_0():
    assert globals.minutes_seconds(time=0) == "0:00"


def test_minutes_seconds_of_1():
    assert globals.minutes_seconds(time=1) == "0:01"


def test_minutes_seconds_of_59():
    assert globals.minutes_seconds(time=59) == "0:59"


def test_minutes_seconds_of_60():
    assert globals.minutes_seconds(time=60) == "1:00"


def test_minutes_seconds_of_600():
    assert globals.minutes_seconds(time=600) == "10:00"


def test_minutes_seconds_of_6000():
    assert globals.minutes_seconds(time=6000) == "100:00"


def test_minutes_seconds_of_minus_1():
    assert globals.minutes_seconds(time=-1) == "-0:01"


def test_minutes_seconds_of_minus_59():
    assert globals.minutes_seconds(time=-59) == "-0:59"


def test_minutes_seconds_of_minus_60():
    assert globals.minutes_seconds(time=-60) == "-1:00"


def test_minutes_seconds_of_minus_600():
    assert globals.minutes_seconds(time=-600) == "-10:00"


def test_minutes_seconds_of_minus_6000():
    assert globals.minutes_seconds(time=-6000) == "-100:00"

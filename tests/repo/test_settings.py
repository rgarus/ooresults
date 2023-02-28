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


import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.series_type import Settings


@pytest.fixture
def db():
    return SqliteRepo(db=":memory:")


def test_series_settings_defaults(db):
    s = db.get_series_settings()
    assert s == Settings()


def test_series_settings_update_1(db):
    settings = Settings(
        name="Series 1",
        nr_of_best_results=4,
        mode="Proportional 1",
        maximum_points=500,
        decimal_places=3,
    )
    db.update_series_settings(settings=settings)
    s = db.get_series_settings()
    print(s.name, s.nr_of_best_results, s.mode, s.maximum_points, s.decimal_places)
    assert db.get_series_settings() == settings


def test_series_settings_update_2(db):
    settings = Settings(
        name="Series 2",
        nr_of_best_results=None,
        mode="Proportional 2",
        maximum_points=600,
        decimal_places=4,
    )
    db.update_series_settings(settings=settings)
    assert db.get_series_settings() == settings


def test_series_settings_updates(db):
    settings = Settings(
        name="Series 1",
        nr_of_best_results=4,
        mode="Proportional 1",
        maximum_points=500,
        decimal_places=3,
    )
    db.update_series_settings(settings=settings)
    settings = Settings(
        name="Series 2",
        nr_of_best_results=None,
        mode="Proportional 2",
        maximum_points=600,
        decimal_places=4,
    )
    db.update_series_settings(settings=settings)
    assert db.get_series_settings() == settings

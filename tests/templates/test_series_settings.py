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

from ooresults.otypes.series_type import Settings
from ooresults.utils import render
from tests.templates.conftest import Html


@pytest.fixture()
def settings() -> Settings:
    return Settings()


def test_series_is_not_none(settings: Settings) -> None:
    html = Html(text=render.series_settings(settings=settings))

    input_name = html.find(path=".//input[@name='name']")
    assert input_name.attrib["value"] == ""

    input_nr_of_best_results = html.find(path=".//input[@name='nr_of_best_results']")
    assert input_nr_of_best_results.attrib["value"] == ""

    options_mode = html.findall(path=".//select[@name='mode']/option")
    assert len(options_mode) == 1
    assert options_mode[0].attrib == {"value": "Proportional", "selected": "selected"}
    assert options_mode[0].text == "Proportional"

    input_maximum_points = html.find(path=".//input[@name='maximum_points']")
    assert input_maximum_points.attrib["value"] == "100"

    input_decimal_places = html.find(path=".//input[@name='decimal_places']")
    assert input_decimal_places.attrib["value"] == "2"


def test_name_is_unequal_default(settings: Settings) -> None:
    settings.name = "Munich O-Cup"
    html = Html(text=render.series_settings(settings=settings))

    input_name = html.find(path=".//input[@name='name']")
    assert input_name.attrib["value"] == "Munich O-Cup"


def test_nr_of_best_results_is_defined(settings: Settings) -> None:
    settings.nr_of_best_results = 3
    html = Html(text=render.series_settings(settings=settings))

    input_nr_of_best_results = html.find(path=".//input[@name='nr_of_best_results']")
    assert input_nr_of_best_results.attrib["value"] == "3"


def test_maximum_points_is_unequal_default(settings: Settings) -> None:
    settings.maximum_points = 1000
    html = Html(text=render.series_settings(settings=settings))

    input_maximum_points = html.find(path=".//input[@name='maximum_points']")
    assert input_maximum_points.attrib["value"] == "1000"


def test_decimal_places_is_unequal_default(settings: Settings) -> None:
    settings.decimal_places = 3
    html = Html(text=render.series_settings(settings=settings))

    input_decimal_places = html.find(path=".//input[@name='decimal_places']")
    assert input_decimal_places.attrib["value"] == "3"

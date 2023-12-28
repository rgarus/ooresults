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


import pathlib

import pytest
import web
from lxml import etree

import ooresults
from ooresults.repo.series_type import Settings
from ooresults.utils.globals import t_globals


@pytest.fixture()
def render():
    templates = pathlib.Path(ooresults.__file__).resolve().parent / "templates"
    return web.template.render(templates, globals=t_globals)


def test_series_settings_1(render):
    settings = Settings(
        name="Munich O-Cup",
        nr_of_best_results=None,
        mode="Proportional",
        maximum_points=1000,
        decimal_places=3,
    )
    html = etree.HTML(str(render.series_settings(settings)))

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "Munich O-Cup"

    input_nr_of_best_results = html.find(".//input[@name='nr_of_best_results']")
    assert input_nr_of_best_results.attrib["value"] == ""

    options_mode = html.findall(".//select[@name='mode']/option")
    assert len(options_mode) == 1
    assert options_mode[0].attrib == {"value": "Proportional", "selected": "selected"}
    assert options_mode[0].text == "Proportional"

    input_maximum_points = html.find(".//input[@name='maximum_points']")
    assert input_maximum_points.attrib["value"] == "1000"

    input_decimal_places = html.find(".//input[@name='decimal_places']")
    assert input_decimal_places.attrib["value"] == "3"


def test_series_settings_2(render):
    settings = Settings(
        name="O-Night",
        nr_of_best_results=3,
        mode="Proportional",
        maximum_points=100,
        decimal_places=2,
    )
    html = etree.HTML(str(render.series_settings(settings)))

    input_name = html.find(".//input[@name='name']")
    assert input_name.attrib["value"] == "O-Night"

    input_nr_of_best_results = html.find(".//input[@name='nr_of_best_results']")
    assert input_nr_of_best_results.attrib["value"] == "3"

    options_mode = html.findall(".//select[@name='mode']/option")
    assert len(options_mode) == 1
    assert options_mode[0].attrib == {"value": "Proportional", "selected": "selected"}
    assert options_mode[0].text == "Proportional"

    input_maximum_points = html.find(".//input[@name='maximum_points']")
    assert input_maximum_points.attrib["value"] == "100"

    input_decimal_places = html.find(".//input[@name='decimal_places']")
    assert input_decimal_places.attrib["value"] == "2"

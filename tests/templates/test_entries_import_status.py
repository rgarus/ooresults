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


from lxml import etree

from ooresults.utils import render


def test_number_of_entries():
    html = etree.HTML(
        render.entries_import_status(
            number_of_imported_entries=13,
            number_of_entries=15,
            names=set(),
        )
    )
    assert html.find(".//p[1]").text == "13 of 15 entries imported."
    assert len(html.findall(".//p")) == 1


def test_names():
    html = etree.HTML(
        render.entries_import_status(
            number_of_imported_entries=13,
            number_of_entries=15,
            names={("Merkel", "Angela"), ("Derkel", "Sabine")},
        )
    )

    assert html.find(".//p[1]").text == "13 of 15 entries imported."
    n1 = html.find(".//ul/li[1]").text
    n2 = html.find(".//ul/li[2]").text
    assert n1 in ("Merkel, Angela", "Derkel, Sabine")
    assert n2 in ("Merkel, Angela", "Derkel, Sabine")
    assert n1 != n2
    assert len(html.findall(".//li")) == 2

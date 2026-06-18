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


from ooresults.utils import render
from tests.templates.conftest import Html


def test_number_of_entries() -> None:
    html = Html(
        text=render.entries_import_status(
            number_of_imported_entries=13,
            number_of_entries=15,
            names=set(),
        )
    )

    elem = html.find(path=".//p[1]")
    assert elem.text == "13 of 15 entries imported."

    assert len(html.findall(path=".//p")) == 1


def test_names() -> None:
    html = Html(
        text=render.entries_import_status(
            number_of_imported_entries=13,
            number_of_entries=15,
            names={("Merkel", "Angela"), ("Derkel", "Sabine")},
        )
    )

    elem = html.find(path=".//p[1]")
    assert elem.text == "13 of 15 entries imported."

    n1 = html.find(path=".//ul/li[1]")
    n2 = html.find(path=".//ul/li[2]")
    assert n1.text in ("Merkel, Angela", "Derkel, Sabine")
    assert n2.text in ("Merkel, Angela", "Derkel, Sabine")
    assert n1.text != n2.text

    assert len(html.findall(path=".//li")) == 2

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
import tempfile

from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Classes"
EVENT_DATE = "2023-12-28"


def test_import_classes(main_page: MainPage, delete_classes: None):
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Class>
    <Name>Bahn A - Männer</Name>
    <ShortName>Männer A</ShortName>
  </Class>
  <Class>
    <Name>Bahn A - Frauen</Name>
    <ShortName>Frauen A</ShortName>
  </Class>
</ClassList>
"""
    class_page = main_page.goto_classes()

    dialog = class_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "ClassData.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_(path=path)

    # check number of rows
    assert class_page.table.nr_of_rows() == 3
    assert class_page.table.nr_of_columns() == 11

    assert class_page.table.row(i=1) == [
        "Classes  (2)",
    ]
    assert class_page.table.row(i=2) == [
        "Bahn A - Frauen",
        "Frauen A",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]
    assert class_page.table.row(i=3) == [
        "Bahn A - Männer",
        "Männer A",
        "",
        "",
        "Standard",
        "If punched",
        "",
        "",
        "",
        "",
        "",
    ]

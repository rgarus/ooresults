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

import pytest
from selenium import webdriver

from webtests.pageobjects.classes import ClassPage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.tabs import Tabs


EVENT_NAME = "Test for Classes"
EVENT_DATE = "2023-12-28"


@pytest.fixture(scope="module")
def select_event(page: webdriver.Remote) -> None:
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()
    dialog = event_page.actions.add()
    dialog.enter_values(
        name=EVENT_NAME,
        date=EVENT_DATE,
    )
    dialog.submit()
    event_page.table.select_row(2)
    yield
    Tabs(page=page).select(text="Events")
    event_page = EventPage(page=page)
    event_page.delete_events()


@pytest.fixture
def class_page(page: webdriver.Remote, select_event: None) -> ClassPage:
    Tabs(page=page).select(text="Classes")
    return ClassPage(page=page)


@pytest.fixture
def delete_classes(class_page: ClassPage) -> None:
    class_page.delete_classes()


def test_import_classes(class_page: ClassPage, delete_classes: None):
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

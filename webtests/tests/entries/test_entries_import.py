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
from collections.abc import Iterator

import pytest

from webtests.controls.alert_window import AlertWindow
from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-12-28"


@pytest.fixture
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture
def event(main_page: MainPage, delete_all: None) -> Iterator[str]:
    event_page = main_page.goto_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE)
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


def test_import_entries(main_page: MainPage, event: str) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Baerbock</Family>
        <Given>Annalena</Given>
      </Name>
      <BirthDate>1980-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Grün</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7379879</ControlCard>
    <Class>
      <Name>Bahn A - Frauen</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person sex="M">
      <Name>
        <Family>Habeck</Family>
        <Given>Robert</Given>
      </Name>
      <BirthDate>1969-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Grün</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7509749</ControlCard>
    <Class>
      <Name>Bahn A - Männer</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person sex="M">
      <Name>
        <Family>Scholz</Family>
        <Given>Olaf</Given>
      </Name>
      <BirthDate>1958-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Rot</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7579050</ControlCard>
    <Class>
      <Name>Bahn A - Männer</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "EntryList.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path)

    # check number of rows
    assert entry_page.table.nr_of_rows() == 4
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (3)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]
    assert entry_page.table.row(i=3) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
        "Bahn A - Männer",
        "",
        "",
        "",
    ]
    assert entry_page.table.row(i=4) == [
        "",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
        "Bahn A - Männer",
        "",
        "",
        "",
    ]


def test_if_a_competitor_is_contained_several_times_then_only_the_first_entry_is_imported(
    main_page: MainPage, event: str
) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Baerbock</Family>
        <Given>Annalena</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Frauen</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Baerbock</Family>
        <Given>Annalena</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Elite</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "EntryList.xml"
        with open(path, mode="w") as f:
            f.write(content)
        info_dialog = dialog.import_file(path=path, info_or_error_dialog="info")
    assert info_dialog.get_text() == [
        "1 of 2 entries imported.",
        "Warning:",
        "For the following names with several entries only the first entry was imported:",
    ]
    info_dialog.close()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 2
    assert entry_page.table.nr_of_columns() == 11

    assert entry_page.table.row(i=1) == [
        "Entries  (1)",
    ]
    assert entry_page.table.row(i=2) == [
        "",
        "Annalena",
        "Baerbock",
        "F",
        "",
        "",
        "",
        "Bahn A - Frauen",
        "",
        "",
        "",
    ]


def test_if_import_entry_list_with_xml_errors_then_an_error_message_is_displayed(
    main_page: MainPage, event: str
) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Even>
</EntryList>
"""
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "EntryList.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, info_or_error_dialog="error")

    # check error message
    alert = AlertWindow(driver=entry_page.driver)
    assert (
        alert.get_text()
        == "Opening and ending tag mismatch: "
        + "Event line 3 and Even, line 8, column 10 (<string>, line 8)"
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 0


def test_if_import_entry_list_with_schema_errors_then_an_error_message_is_displayed(
    main_page: MainPage, event: str
) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>"2023-123-28"</Date>
    </StartTime>
  </Event>
</EntryList>
"""
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "EntryList.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, info_or_error_dialog="error")

    # check error message
    alert = AlertWindow(driver=entry_page.driver)
    assert (
        alert.get_text()
        == "<string>:6:0:ERROR:SCHEMASV:SCHEMAV_CVC_DATATYPE_VALID_1_2_1: "
        + "Element '{http://www.orienteering.org/datastandard/3.0}Date': "
        + "'\"2023-123-28\"' is not a valid value of the atomic type 'xs:date'."
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 0


def test_if_import_entry_list_but_root_tag_is_not_entry_list_then_an_error_message_is_displayed(
    main_page: MainPage, event: str
) -> None:
    content = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<ResultList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>{EVENT_NAME}</Name>
    <StartTime>
      <Date>{EVENT_DATE}</Date>
    </StartTime>
  </Event>
</ResultList>
"""
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "EntryList.xml"
        with open(path, mode="w") as f:
            f.write(content)
        dialog.import_file(path=path, info_or_error_dialog="error")

    # check error message
    alert = AlertWindow(driver=entry_page.driver)
    assert (
        alert.get_text()
        == "Root element is {http://www.orienteering.org/datastandard/3.0}ResultList "
        + "but should be EntryList"
    )
    alert.accept()
    dialog.cancel()

    # check number of rows
    assert entry_page.table.nr_of_rows() == 0

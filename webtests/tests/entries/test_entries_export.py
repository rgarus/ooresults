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


from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from lxml import etree

import ooresults
from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for exporting Entries"
EVENT_DATE = "2023-12-28"


schema_file = Path(ooresults.__file__).parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


@pytest.fixture(scope="module")
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture(scope="module")
def event(main_page: MainPage, delete_all: None) -> Iterator[str]:
    event_page = main_page.goto_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE)
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


@pytest.fixture(scope="module")
def import_entry_list(main_page: MainPage, event: str) -> None:
    entry_list_path = Path(__file__).parent.parent / "data" / "EntryList.xml"
    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    dialog.import_file(path=entry_list_path)


def test_export_entries_as_iof_entry_list(
    main_page: MainPage, event: str, import_entry_list: None, download_dir: Path
) -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>Test for exporting Entries</Name>
    <StartTime>
      <Date>2023-12-28</Date>
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
        <Family>Buschmann</Family>
        <Given>Marco</Given>
      </Name>
      <BirthDate>1977-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Gelb</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7076815</ControlCard>
    <Class>
      <Name>Bahn A - Männer</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Faeser</Family>
        <Given>Nancy</Given>
      </Name>
      <BirthDate>1970-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Rot</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7040504</ControlCard>
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
        <Family>Lindner</Family>
        <Given>Christian</Given>
      </Name>
      <BirthDate>1979-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Gelb</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">7754987</ControlCard>
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
    entry_page = main_page.goto_entries()
    dialog = entry_page.actions.export()
    dialog.format().select(text=dialog.ENTRY_LIST)
    t1 = datetime.now()
    document = dialog.export(download_dir=download_dir)
    t2 = datetime.now()

    assert xml_schema.validate(etree.XML(document))
    root_1 = etree.XML(document)
    root_2 = etree.XML(content.encode(encoding="utf8"))

    create_time = root_1.attrib.pop("createTime", None)
    t1 = t1.replace(microsecond=t1.microsecond // 1000 * 1000)
    t2 = t2.replace(microsecond=t2.microsecond // 1000 * 1000)
    assert create_time is not None and t1 <= datetime.fromisoformat(create_time) <= t2

    text_1 = etree.tostring(root_1, encoding="UTF-8", xml_declaration=True)
    text_2 = etree.tostring(root_2, encoding="UTF-8", xml_declaration=True)
    assert text_1 == text_2

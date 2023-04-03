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


import datetime

from ooresults.plugins import iof_entry_list
from ooresults.repo import result_type


def test_import_entry_list_with_one_entry():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
      <BirthDate>1972-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Kanzleramt</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">1234567</ControlCard>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    event, entries = iof_entry_list.parse_entry_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
    }
    assert entries == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
            "result": result_type.PersonRaceResult(),
        },
    ]


def test_export_entry_list_with_one_entry():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person sex="F">
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
      <BirthDate>1972-01-01</BirthDate>
    </Person>
    <Organisation>
      <Name>OC Kanzleramt</Name>
    </Organisation>
    <ControlCard punchingSystem="SI">1234567</ControlCard>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    document = iof_entry_list.create_entry_list(
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "class_": "Bahn A - Lang",
                "club": "OC Kanzleramt",
                "chip": "1234567",
                "gender": "F",
                "year": 1972,
                "result": result_type.PersonRaceResult(),
            },
        ],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_entry_list_without_person_entries():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</EntryList>
"""
    event, entries = iof_entry_list.parse_entry_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
    }
    assert entries == []


def test_export_entry_list_without_person_entries():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
</EntryList>
"""
    document = iof_entry_list.create_entry_list(
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [],
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_entry_list_with_several_entries():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Claudia</Given>
      </Name>
    </Person>
    <ControlCard punchingSystem="SI">1234567</ControlCard>
    <Class>
      <Name>Bahn B - Mittel</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Birgit</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    event, entries = iof_entry_list.parse_entry_list(bytes(content, encoding="utf-8"))
    assert event == {
        "name": "1. O-Cup 2020",
        "date": datetime.date(year=2020, month=2, day=9),
    }
    assert entries == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
            "result": result_type.PersonRaceResult(),
        },
        {
            "first_name": "Claudia",
            "last_name": "Merkel",
            "class_": "Bahn B - Mittel",
            "club": "",
            "chip": "1234567",
            "gender": "",
            "year": None,
            "result": result_type.PersonRaceResult(),
        },
        {
            "first_name": "Birgit",
            "last_name": "Merkel",
            "class_": "Bahn A - Lang",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
            "result": result_type.PersonRaceResult(),
        },
    ]


def test_export_entry_list_with_several_entries():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<EntryList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Event>
    <Name>1. O-Cup 2020</Name>
    <StartTime>
      <Date>2020-02-09</Date>
    </StartTime>
  </Event>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Claudia</Given>
      </Name>
    </Person>
    <ControlCard punchingSystem="SI">1234567</ControlCard>
    <Class>
      <Name>Bahn B - Mittel</Name>
    </Class>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Birgit</Given>
      </Name>
    </Person>
    <Class>
      <Name>Bahn A - Lang</Name>
    </Class>
  </PersonEntry>
</EntryList>
"""
    document = iof_entry_list.create_entry_list(
        {
            "name": "1. O-Cup 2020",
            "date": datetime.date(year=2020, month=2, day=9),
        },
        [
            {
                "first_name": "Angela",
                "last_name": "Merkel",
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(),
            },
            {
                "first_name": "Claudia",
                "last_name": "Merkel",
                "class_": "Bahn B - Mittel",
                "chip": "1234567",
                "result": result_type.PersonRaceResult(),
            },
            {
                "first_name": "Birgit",
                "last_name": "Merkel",
                "class_": "Bahn A - Lang",
                "result": result_type.PersonRaceResult(),
            },
        ],
    )
    assert document == bytes(content, encoding="utf-8")

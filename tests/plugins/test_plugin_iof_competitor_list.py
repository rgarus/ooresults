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


from tests.competitor import Competitor
from ooresults.plugins import iof_competitor_list


def test_import_name():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CompetitorList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Competitor>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
    </Person>
  </Competitor>
</CompetitorList>
"""
    assert iof_competitor_list.parse_competitor_list(
        bytes(content, encoding="utf-8")
    ) == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
        }
    ]


def test_export_name():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CompetitorList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Competitor>
    <Person>
      <Name>
        <Family>Merkel</Family>
        <Given>Angela</Given>
      </Name>
    </Person>
  </Competitor>
</CompetitorList>
"""
    document = iof_competitor_list.create_competitor_list(
        [
            Competitor(first_name="Angela", last_name="Merkel"),
        ]
    )
    assert document == bytes(content, encoding="utf-8")


def test_import_full():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CompetitorList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Competitor>
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
  </Competitor>
</CompetitorList>
"""
    assert iof_competitor_list.parse_competitor_list(
        bytes(content, encoding="utf-8")
    ) == [
        {
            "first_name": "Angela",
            "last_name": "Merkel",
            "club": "OC Kanzleramt",
            "chip": "1234567",
            "gender": "F",
            "year": 1972,
        }
    ]


def test_export_full():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<CompetitorList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Competitor>
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
  </Competitor>
</CompetitorList>
"""
    document = iof_competitor_list.create_competitor_list(
        [
            Competitor(
                first_name="Angela",
                last_name="Merkel",
                club_name="OC Kanzleramt",
                gender="F",
                year=1972,
                chip="1234567",
            )
        ]
    )
    assert document == bytes(content, encoding="utf-8")

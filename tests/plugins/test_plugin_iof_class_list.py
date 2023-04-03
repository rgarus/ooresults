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


from ooresults.plugins import iof_class_list


def test_import_class_list():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Class>
      <Name>D 14-15</Name>
  </Class>
  <Class>
      <Name>H 14-15</Name>
  </Class>
  <Class>
      <Name>Schüler B</Name>
      <ShortName>SchB</ShortName>
  </Class>
  <Class>
      <Name>Offen Mittel</Name>
      <ShortName>OM</ShortName>
  </Class>
</ClassList>
"""
    classes = iof_class_list.parse_class_list(bytes(content, encoding="utf-8"))
    assert classes == [
        {
            "name": "D 14-15",
            "short_name": None,
        },
        {
            "name": "H 14-15",
            "short_name": None,
        },
        {
            "name": "Schüler B",
            "short_name": "SchB",
        },
        {
            "name": "Offen Mittel",
            "short_name": "OM",
        },
    ]


def test_export_class_list():
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Class>
    <Name>D 14-15</Name>
  </Class>
  <Class>
    <Name>H 14-15</Name>
  </Class>
  <Class>
    <Name>Schüler B</Name>
    <ShortName>SchB</ShortName>
  </Class>
  <Class>
    <Name>Offen Mittel</Name>
    <ShortName>OM</ShortName>
  </Class>
</ClassList>
"""
    document = iof_class_list.create_class_list(
        [
            {
                "name": "D 14-15",
                "short_name": None,
            },
            {
                "name": "H 14-15",
            },
            {
                "name": "Schüler B",
                "short_name": "SchB",
            },
            {
                "name": "Offen Mittel",
                "short_name": "OM",
            },
        ]
    )
    assert document == bytes(content, encoding="utf-8")

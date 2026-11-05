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


from datetime import datetime
from pathlib import Path

import pytest
from lxml import etree

import ooresults
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.plugins import iof_class_list


schema_file = Path(ooresults.__file__).parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


def check_document(document: bytes, content: str, t1: datetime, t2: datetime) -> None:
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


def test_import_if_class_name_is_missing_then_raise_exception() -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Class></Class>
</ClassList>
"""
    with pytest.raises(RuntimeError, match="<string>:3:0:ERROR:SCHEMASV"):
        iof_class_list.parse_class_list(bytes(content, encoding="utf-8"))


def test_import_if_class_name_is_empty_then_raise_exception() -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0">
  <Class>
      <Name></Name>
  </Class>
</ClassList>
"""
    with pytest.raises(RuntimeError, match="Class/Name missing or empty"):
        iof_class_list.parse_class_list(bytes(content, encoding="utf-8"))


def test_import_class_list() -> None:
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


def test_export_class_list() -> None:
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
    t1 = datetime.now()
    document = iof_class_list.create_class_list(
        [
            ClassInfoType(
                id=1,
                name="D 14-15",
                short_name=None,
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=2,
                name="H 14-15",
                short_name=None,
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=3,
                name="Schüler B",
                short_name="SchB",
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=4,
                name="Offen Mittel",
                short_name="OM",
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
        ]
    )
    t2 = datetime.now()
    check_document(document=document, content=content, t1=t1, t2=t2)

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
from webtests.pageobjects.main_page import MainPage


schema_file = Path(ooresults.__file__).parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


@pytest.fixture
def import_class_list(main_page: MainPage, event: str, delete_classes: None) -> None:
    class_list_path = Path(__file__).parent.parent / "data" / "ClassList.xml"
    class_page = main_page.goto_classes(event=event)
    dialog = class_page.actions.import_()
    dialog.import_file(path=class_list_path)


def test_export_classes(
    main_page: MainPage, event: str, import_class_list: None, download_dir: Path
) -> None:
    content = """\
<?xml version='1.0' encoding='UTF-8'?>
<ClassList xmlns="http://www.orienteering.org/datastandard/3.0" iofVersion="3.0" creator="ooresults (https://pypi.org/project/ooresults)">
  <Class>
    <Name>Bahn A - Frauen</Name>
    <ShortName>Frauen</ShortName>
  </Class>
  <Class>
    <Name>Bahn A - Männer</Name>
    <ShortName>Männer</ShortName>
  </Class>
  <Class>
    <Name>Organizer</Name>
  </Class>
</ClassList>
"""
    class_page = main_page.goto_classes()
    dialog = class_page.actions.export()
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

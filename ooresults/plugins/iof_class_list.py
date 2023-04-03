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
from typing import List
from typing import Dict
from typing import Tuple

from lxml import etree
from lxml.builder import ElementMaker


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


iof_namespace = "http://www.orienteering.org/datastandard/3.0"
namespaces = {None: iof_namespace}


def create_class_list(classes: List[Dict]) -> bytes:
    E = ElementMaker(namespace=iof_namespace, nsmap=namespaces)

    CLASSLIST = E.ClassList
    CLASS = E.Class
    NAME = E.Name
    SHORTNAME = E.ShortName

    root = CLASSLIST(
        iofVersion="3.0",
        creator="ooresults (https://pypi.org/project/ooresults)",
    )

    for c in classes:
        class_ = CLASS()
        class_.append(NAME(c["name"]))

        if c.get("short_name", None) is not None:
            class_.append(SHORTNAME(str(c["short_name"])))

        root.append(class_)

    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    return etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )


def parse_class_list(content: bytes) -> Tuple[List[Dict]]:
    # Class: Dict of {'name': str, 'short_name': Optional[str]}

    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + iof_namespace + "}ClassList":
        raise RuntimeError("Root element is " + root.tag + " but should be ClassList")

    classes = []
    class_list = root.findall("Class", namespaces=namespaces)

    for class_ in class_list:
        c = {
            "name": "",
            "short_name": None,
        }
        c["name"] = class_.find("Name", namespaces=namespaces).text

        short_name = class_.find("ShortName", namespaces=namespaces)
        if short_name is not None:
            c["short_name"] = short_name.text

        classes.append(c)

    return classes

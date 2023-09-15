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

from lxml import etree
from lxml.builder import ElementMaker

from ooresults.repo.competitor_type import CompetitorType


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


iof_namespace = "http://www.orienteering.org/datastandard/3.0"
namespaces = {None: iof_namespace}


def create_competitor_list(competitors: List[CompetitorType]) -> bytes:
    E = ElementMaker(namespace=iof_namespace, nsmap=namespaces)

    COMPETITORLIST = E.CompetitorList
    COMPETITOR = E.Competitor
    PERSON = E.Person
    NAME = E.Name
    FAMILY = E.Family
    GIVEN = E.Given
    BIRTHDATE = E.BirthDate
    ORGANISATION = E.Organisation
    CONTROLCARD = E.ControlCard

    root = COMPETITORLIST(
        iofVersion="3.0",
        creator="ooresults (https://pypi.org/project/ooresults)",
    )

    for c in competitors:
        competitor = COMPETITOR()
        person = PERSON(
            NAME(
                FAMILY(c.last_name),
                GIVEN(c.first_name),
            ),
        )
        if c.gender:
            person.set("sex", c.gender)
        if c.year is not None:
            person.append(BIRTHDATE(str(c.year) + "-01-01"))
        competitor.append(person)
        if c.club_name:
            competitor.append(ORGANISATION(NAME(c.club_name)))
        if c.chip:
            competitor.append(CONTROLCARD(c.chip, punchingSystem="SI"))
        root.append(competitor)

    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    return etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )


def parse_competitor_list(content: bytes) -> List[Dict]:
    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + iof_namespace + "}CompetitorList":
        raise RuntimeError(
            "Root element is " + root.tag + " but should be CompetitorList"
        )

    result = []
    competitors = root.findall("Competitor", namespaces=namespaces)
    for c in competitors:
        print(c.tag)
        for i in c:
            print(i.tag)
        r = {
            "first_name": "",
            "last_name": "",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
        }

        r["last_name"] = c.find("Person/Name/Family", namespaces=namespaces).text
        r["first_name"] = c.find("Person/Name/Given", namespaces=namespaces).text

        e_person = c.find("Person", namespaces=namespaces)
        if e_person.get("sex") is not None:
            r["gender"] = e_person.get("sex")
        e_birthdate = c.find("Person/BirthDate", namespaces=namespaces)
        if e_birthdate is not None:
            r["year"] = int(e_birthdate.text[0:4])
        e_organization = c.find("Organisation/Name", namespaces=namespaces)
        if e_organization is not None:
            r["club"] = e_organization.text
        e_controlcard = c.find("ControlCard", namespaces=namespaces)
        if e_controlcard is not None:
            r["chip"] = e_controlcard.text

        result.append(r)

    return result

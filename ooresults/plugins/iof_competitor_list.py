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

from lxml import etree
from lxml.builder import ElementMaker

from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.competitor_type import Sex
from ooresults.plugins.import_types.competitor_dict import CompetitorDict


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


IOF_NAMESPACE = "http://www.orienteering.org/datastandard/3.0"
NSMAP = {None: IOF_NAMESPACE}


def create_competitor_list(competitors: list[CompetitorType]) -> bytes:
    E = ElementMaker(namespace=IOF_NAMESPACE, nsmap=NSMAP)

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
        if c.sex:
            person.set("sex", c.sex.value)
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


def parse_competitor_list(content: bytes) -> list[CompetitorDict]:
    NS = {"": IOF_NAMESPACE}

    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + IOF_NAMESPACE + "}CompetitorList":
        raise RuntimeError(
            f"Root element is {str(root.tag)} but should be CompetitorList"
        )

    result: list[CompetitorDict] = []
    competitors = root.findall("Competitor", namespaces=NS)
    for c in competitors:
        r: CompetitorDict = {
            "first_name": "",
            "last_name": "",
            "club": "",
            "chip": "",
            "sex": None,
            "year": None,
        }

        e_family = c.find("Person/Name/Family", namespaces=NS)
        if e_family is not None and (text := e_family.text):
            r["last_name"] = text
        else:
            raise RuntimeError("Person/Name/Family missing or empty")
        e_given = c.find("Person/Name/Given", namespaces=NS)
        if e_given is not None and (text := e_given.text):
            r["first_name"] = text
        else:
            raise RuntimeError("Person/Name/Given missing or empty")

        e_person = c.find("Person", namespaces=NS)
        if e_person is not None and (sex := e_person.get("sex")):
            r["sex"] = Sex(sex)
        e_birthdate = c.find("Person/BirthDate", namespaces=NS)
        if e_birthdate is not None and (text := e_birthdate.text):
            r["year"] = int(text[0:4])
        e_organization = c.find("Organisation/Name", namespaces=NS)
        if e_organization is not None and (text := e_organization.text):
            r["club"] = text
        e_controlcard = c.find("ControlCard", namespaces=NS)
        if e_controlcard is not None and (text := e_controlcard.text):
            r["chip"] = text

        result.append(r)

    return result

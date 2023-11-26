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

import iso8601
from lxml import etree
from lxml.builder import ElementMaker

from ooresults.repo import result_type
from ooresults.repo.entry_type import EntryType
from ooresults.repo.event_type import EventType


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


iof_namespace = "http://www.orienteering.org/datastandard/3.0"
namespaces = {None: iof_namespace}


def create_entry_list(event: EventType, entries: List[EntryType]) -> bytes:
    E = ElementMaker(namespace=iof_namespace, nsmap=namespaces)

    ENTRYLIST = E.EntryList
    EVENT = E.Event
    NAME = E.Name
    STARTTIME = E.StartTime
    DATE = E.Date
    PERSONENTRY = E.PersonEntry
    PERSON = E.Person
    FAMILY = E.Family
    GIVEN = E.Given
    BIRTHDATE = E.BirthDate
    ORGANISATION = E.Organisation
    CONTROLCARD = E.ControlCard
    CLASS = E.Class

    root = ENTRYLIST(
        iofVersion="3.0",
        creator="ooresults (https://pypi.org/project/ooresults)",
    )

    e_event = EVENT()
    e_event.append(NAME(event.name))
    e_event.append(STARTTIME(DATE(event.date.isoformat())))
    root.append(e_event)

    for e in entries:
        # do not export pseudo entries without name
        # (used to store not already assigned sportident results)
        if e.last_name is None:
            continue

        pe = PERSONENTRY()
        person = PERSON(
            NAME(
                FAMILY(e.last_name),
                GIVEN(e.first_name),
            ),
        )
        if e.gender:
            person.set("sex", e.gender)
        if e.year is not None:
            person.append(BIRTHDATE(str(e.year) + "-01-01"))
        pe.append(person)

        if e.club_name:
            pe.append(
                ORGANISATION(
                    NAME(e.club_name),
                ),
            )

        if e.chip:
            pe.append(CONTROLCARD(e.chip, punchingSystem="SI"))
        if e.class_name:
            pe.append(CLASS(NAME(e.class_name)))

        root.append(pe)

    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    return etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )


def parse_entry_list(content: bytes) -> Tuple[Dict, List[Dict]]:
    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + iof_namespace + "}EntryList":
        raise RuntimeError("Root element is " + root.tag + " but should be ResultList")

    event = {}
    event["name"] = root.find("Event/Name", namespaces=namespaces).text
    date = root.find("Event/StartTime/Date", namespaces=namespaces)
    if date is not None:
        event["date"] = iso8601.parse_date(date.text).date()

    entries = []
    person_entry_list = root.findall("PersonEntry", namespaces=namespaces)
    for pe in person_entry_list:
        e = {
            "first_name": "",
            "last_name": "",
            "class_": "",
            "club": "",
            "chip": "",
            "gender": "",
            "year": None,
            "result": result_type.PersonRaceResult(),
        }

        e["last_name"] = pe.find("Person/Name/Family", namespaces=namespaces).text
        e["first_name"] = pe.find("Person/Name/Given", namespaces=namespaces).text

        e_person = pe.find("Person", namespaces=namespaces)
        if e_person.get("sex") is not None:
            e["gender"] = e_person.get("sex")
        e_birthdate = pe.find("Person/BirthDate", namespaces=namespaces)
        if e_birthdate is not None:
            e["year"] = int(e_birthdate.text[0:4])

        e_organization = pe.find("Organisation/Name", namespaces=namespaces)
        if e_organization is not None:
            e["club"] = e_organization.text

        e_controlcard = pe.find("ControlCard", namespaces=namespaces)
        if e_controlcard is not None:
            e["chip"] = e_controlcard.text
        e_class = pe.find("Class/Name", namespaces=namespaces)
        if e_class is not None:
            e["class_"] = e_class.text

        entries.append(e)

    return event, entries

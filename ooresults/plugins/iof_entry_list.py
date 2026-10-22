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

import iso8601
from lxml import etree
from lxml.builder import ElementMaker

from ooresults.otypes import result_type
from ooresults.otypes.competitor_type import Sex
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType
from ooresults.plugins.import_types.entry_dict import EntryDict
from ooresults.plugins.import_types.event_dict import EventDict


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


IOF_NAMESPACE = "http://www.orienteering.org/datastandard/3.0"
NSMAP = {None: IOF_NAMESPACE}


def create_entry_list(event: EventType, entries: list[EntryType]) -> bytes:
    E = ElementMaker(namespace=IOF_NAMESPACE, nsmap=NSMAP)

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
        if e.last_name is None or e.first_name is None:
            continue

        pe = PERSONENTRY()
        person = PERSON(
            NAME(
                FAMILY(e.last_name),
                GIVEN(e.first_name),
            ),
        )
        if e.sex:
            person.set("sex", e.sex.value)
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


def parse_entry_list(content: bytes) -> tuple[EventDict, list[EntryDict]]:
    NS = {"": IOF_NAMESPACE}

    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + IOF_NAMESPACE + "}EntryList":
        raise RuntimeError(f"Root element is {str(root.tag)} but should be EntryList")

    event = EventDict(name="", date=None)
    name = root.find("Event/Name", namespaces=NS)
    if name is not None and (text := name.text):
        event["name"] = text
    else:
        raise RuntimeError("Event/Name missing or empty")

    date = root.find("Event/StartTime/Date", namespaces=NS)
    if date is not None and (text := date.text):
        event["date"] = iso8601.parse_date(text).date()

    entries = []
    person_entry_list = root.findall("PersonEntry", namespaces=NS)
    for pe in person_entry_list:
        e: EntryDict = {
            "first_name": "",
            "last_name": "",
            "class_": "",
            "club": "",
            "chip": "",
            "sex": None,
            "year": None,
            "result": result_type.PersonRaceResult(),
        }

        e_family = pe.find("Person/Name/Family", namespaces=NS)
        if e_family is not None and (text := e_family.text):
            e["last_name"] = text
        else:
            raise RuntimeError("Person/Name/Family missing or empty")
        e_given = pe.find("Person/Name/Given", namespaces=NS)
        if e_given is not None and (text := e_given.text):
            e["first_name"] = text
        else:
            raise RuntimeError("Person/Name/Given missing or empty")

        e_person = pe.find("Person", namespaces=NS)
        if e_person is not None and (sex := e_person.get("sex")):
            e["sex"] = Sex(sex)
        e_birthdate = pe.find("Person/BirthDate", namespaces=NS)
        if e_birthdate is not None and (text := e_birthdate.text):
            e["year"] = int(text[0:4])
        e_organization = pe.find("Organisation/Name", namespaces=NS)
        if e_organization is not None and (text := e_organization.text):
            e["club"] = text
        e_controlcard = pe.find("ControlCard", namespaces=NS)
        if e_controlcard is not None and (text := e_controlcard.text):
            e["chip"] = text
        e_class = pe.find("Class/Name", namespaces=NS)
        if e_class is not None and (text := e_class.text):
            e["class_"] = text

        entries.append(e)

    return event, entries

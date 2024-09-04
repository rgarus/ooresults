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
from datetime import timedelta
from enum import Enum
from typing import List
from typing import Dict
from typing import Tuple
from typing import Optional

from lxml import etree
from lxml.builder import ElementMaker
import iso8601

from ooresults.repo import result_type
from ooresults.repo import start_type
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SpStatus


schema_file = pathlib.Path(__file__).parent.parent / "schema" / "IOF.xsd"
xml_schema = etree.XMLSchema(etree.parse(str(schema_file)))


iof_namespace = "http://www.orienteering.org/datastandard/3.0"
namespaces = {None: iof_namespace}


class ResultListStatus(Enum):
    """
    Complete:
        The result list is complete, i.e. all competitors are included.
        Used for official results after the event.
    Delta:
        The result list only contains changes since last list.
        Used for frequent exchange of results.
    Snapshot:
        The result list is a snapshot of the current standings.
        Used while the event is under way.
    """

    COMPLETE = "Complete"
    DELTA = "Delta"
    SNAPSHOT = "Snapshot"


def create_result_list(
    event: EventType,
    class_results: List[Tuple[ClassInfoType, List[RankedEntryType]]],
    status: Optional[ResultListStatus] = None,
) -> bytes:
    E = ElementMaker(namespace=iof_namespace, nsmap=namespaces)

    RESULTLIST = E.ResultList
    EVENT = E.Event
    NAME = E.Name
    STARTTIME = E.StartTime
    DATE = E.Date
    CLASSRESULT = E.ClassResult
    CLASS = E.Class
    COURSE = E.Course
    LENGTH = E.Length
    CLIMB = E.Climb
    NUMBEROFCONTROLS = E.NumberOfControls
    PERSONRESULT = E.PersonResult
    PERSON = E.Person
    FAMILY = E.Family
    GIVEN = E.Given
    BIRTHDATE = E.BirthDate
    ORGANISATION = E.Organisation
    RESULT = E.Result
    CONTROLCARD = E.ControlCard
    POSITION = E.Position
    STATUS = E.Status
    STARTTIME = E.StartTime
    FINISHTIME = E.FinishTime
    TIME = E.Time
    TIMEBEHIND = E.TimeBehind
    SPLITTIME = E.SplitTime
    CONTROLCODE = E.ControlCode

    root = RESULTLIST(
        iofVersion="3.0",
        creator="ooresults (https://pypi.org/project/ooresults)",
    )
    if status is not None:
        root.attrib["status"] = status.value

    e_event = EVENT()
    e_event.append(NAME(event.name))
    e_event.append(STARTTIME(DATE(event.date.isoformat())))
    root.append(e_event)

    for class_, ranked_results in class_results:
        if not ranked_results:
            continue

        cr = CLASSRESULT()
        cr.append(CLASS(NAME(class_.name)))

        co = COURSE()
        if class_.course_name:
            co.append(NAME(class_.course_name))
        if class_.course_length is not None:
            co.append(LENGTH(str(round(class_.course_length))))
        if class_.course_climb is not None:
            co.append(CLIMB(str(round(class_.course_climb))))
        if class_.number_of_controls is not None and class_.number_of_controls > 0:
            co.append(NUMBEROFCONTROLS(str(class_.number_of_controls)))
        if len(co):
            cr.append(co)

        for ranked_result in ranked_results:
            entry = ranked_result.entry
            result = entry.result

            pr = PERSONRESULT()
            person = PERSON(
                NAME(
                    FAMILY(entry.last_name),
                    GIVEN(entry.first_name),
                ),
            )
            if entry.gender:
                person.set("sex", entry.gender)
            if entry.year is not None:
                person.append(BIRTHDATE(str(entry.year) + "-01-01"))
            pr.append(person)

            if entry.club_name:
                pr.append(
                    ORGANISATION(
                        NAME(entry.club_name),
                    ),
                )

            res = RESULT()
            if result.start_time is not None:
                res.append(STARTTIME(result.start_time.isoformat(timespec="seconds")))
            if result.finish_time is not None:
                res.append(FINISHTIME(result.finish_time.isoformat(timespec="seconds")))
            if result.time is not None:
                res.append(TIME(str(result.time)))

            if result.status == ResultStatus.OK:
                if entry.not_competing:
                    res.append(STATUS("NotCompeting"))
                else:
                    if ranked_result.time_behind is not None:
                        res.append(TIMEBEHIND(str(ranked_result.time_behind)))

                    if ranked_result.rank is not None:
                        res.append(POSITION(str(ranked_result.rank)))
                    res.append(STATUS("OK"))
            else:
                res.append(
                    STATUS(
                        {
                            ResultStatus.INACTIVE: "Inactive",
                            ResultStatus.ACTIVE: "Active",
                            ResultStatus.OK: "OK",
                            ResultStatus.MISSING_PUNCH: "MissingPunch",
                            ResultStatus.DID_NOT_START: "DidNotStart",
                            ResultStatus.DID_NOT_FINISH: "DidNotFinish",
                            ResultStatus.DISQUALIFIED: "Disqualified",
                            ResultStatus.OVER_TIME: "OverTime",
                            ResultStatus.FINISHED: "Finished",
                        }[result.status]
                    )
                )
            for s in result.split_times:
                if s.status is not None:
                    split_time = SPLITTIME(CONTROLCODE(s.control_code))
                    if s.status != SpStatus.OK:
                        SPSTATUS = {
                            SpStatus.OK: "OK",
                            SpStatus.MISSING: "Missing",
                            SpStatus.ADDITIONAL: "Additional",
                        }
                        split_time.set("status", SPSTATUS[s.status])
                    if s.time is not None:
                        split_time.append(TIME(str(s.time)))
                    res.append(split_time)
            if entry.chip:
                res.append(CONTROLCARD(entry.chip, punchingSystem="SI"))
            pr.append(res)
            cr.append(pr)
        root.append(cr)

    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    return etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )


STATUS_MAP = {
    "OK": ResultStatus.OK,
    "Finished": ResultStatus.FINISHED,
    "MissingPunch": ResultStatus.MISSING_PUNCH,
    "Disqualified": ResultStatus.DISQUALIFIED,
    "DidNotFinish": ResultStatus.DID_NOT_FINISH,
    "Active": ResultStatus.ACTIVE,
    "Inactive": ResultStatus.INACTIVE,
    "OverTime": ResultStatus.OVER_TIME,
    "SportingWithdrawal": ResultStatus.DID_NOT_FINISH,
    "NotCompeting": ResultStatus.OK,
    "Moved": ResultStatus.INACTIVE,
    "MovedUp": ResultStatus.INACTIVE,
    "DidNotStart": ResultStatus.DID_NOT_START,
    "DidNotEnter": ResultStatus.INACTIVE,
    "Cancelled": ResultStatus.INACTIVE,
}


SPSTATUS_MAP = {
    "OK": SpStatus.OK,
    "Missing": SpStatus.MISSING,
    "Additional": SpStatus.ADDITIONAL,
}


def parse_result_list(
    content: bytes,
) -> Tuple[Dict, List[Dict], Optional[ResultListStatus]]:
    root = etree.XML(content)
    if not xml_schema.validate(root):
        raise RuntimeError(xml_schema.error_log.last_error)
    if not root.tag == "{" + iof_namespace + "}ResultList":
        raise RuntimeError("Root element is " + root.tag + " but should be ResultList")

    result_list_status = root.attrib.get("status", None)
    if result_list_status is not None:
        result_list_status = ResultListStatus(result_list_status)

    event = {}
    event["name"] = root.find("Event/Name", namespaces=namespaces).text
    date = root.find("Event/StartTime/Date", namespaces=namespaces)
    if date is not None:
        event["date"] = iso8601.parse_date(date.text).date()

    result = []
    class_result_list = root.findall("ClassResult", namespaces=namespaces)
    for c in class_result_list:
        class_ = c.find("Class/Name", namespaces=namespaces).text
        person_result_list = c.findall("PersonResult", namespaces=namespaces)
        for pr in person_result_list:
            r = {
                "first_name": pr.find("Person/Name/Given", namespaces=namespaces).text,
                "last_name": pr.find("Person/Name/Family", namespaces=namespaces).text,
                "class_": class_,
                "club": "",
                "chip": "",
                "gender": "",
                "year": None,
                "not_competing": False,
                "result": result_type.PersonRaceResult(),
            }

            e_person = pr.find("Person", namespaces=namespaces)
            if e_person.get("sex") is not None:
                r["gender"] = e_person.get("sex")
            e_birthdate = pr.find("Person/BirthDate", namespaces=namespaces)
            if e_birthdate is not None:
                r["year"] = int(e_birthdate.text[0:4])

            e_organization = pr.find("Organisation/Name", namespaces=namespaces)
            if e_organization is not None:
                r["club"] = e_organization.text

            e_result = pr.find("Result", namespaces=namespaces)
            e_controlcard = e_result.find("ControlCard", namespaces=namespaces)
            if e_controlcard is not None:
                r["chip"] = e_controlcard.text

            e_status = e_result.find("Status", namespaces=namespaces)
            r["result"].status = STATUS_MAP[e_status.text]
            if e_status.text == "NotCompeting":
                r["not_competing"] = True

            e_start_time = e_result.find("StartTime", namespaces=namespaces)
            if e_start_time is not None:
                if r["result"].status in [
                    ResultStatus.INACTIVE,
                    ResultStatus.ACTIVE,
                    ResultStatus.DID_NOT_START,
                ]:
                    r["start"] = start_type.PersonRaceStart(
                        start_time=iso8601.parse_date(e_start_time.text)
                    )
                else:
                    r["result"].start_time = iso8601.parse_date(e_start_time.text)
                    r["result"].punched_start_time = r["result"].start_time
                    r["result"].si_punched_start_time = r["result"].start_time
            e_finish_time = e_result.find("FinishTime", namespaces=namespaces)
            if e_finish_time is not None:
                r["result"].finish_time = iso8601.parse_date(e_finish_time.text)
                r["result"].punched_finish_time = r["result"].finish_time
                r["result"].si_punched_finish_time = r["result"].finish_time
            e_time = e_result.find("Time", namespaces=namespaces)
            if e_time is not None:
                r["result"].time = int(e_time.text)

            e_split_time_list = e_result.findall("SplitTime", namespaces=namespaces)
            for e_split_time in e_split_time_list:
                split_time = result_type.SplitTime(
                    control_code=e_split_time.find(
                        "ControlCode", namespaces=namespaces
                    ).text,
                    status=SPSTATUS_MAP[e_split_time.get("status", "OK")],
                )
                e_time = e_split_time.find("Time", namespaces=namespaces)
                if e_time is not None:
                    split_time.time = int(e_time.text)
                    if r["result"].start_time:
                        t = r["result"].start_time + timedelta(seconds=split_time.time)
                        split_time.punch_time = t
                        split_time.si_punch_time = t
                elif split_time.status == SpStatus.OK:
                    split_time.punch_time = result_type.SplitTime.NO_TIME
                r["result"].split_times.append(split_time)

            result.append(r)

    return event, result, result_list_status

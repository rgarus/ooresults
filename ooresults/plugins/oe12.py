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


import io
from typing import List
from typing import Dict

import clevercsv as csv
from unidecode import unidecode

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import ResultStatus


def cp1252(value: str) -> str:
    try:
        _ = value.encode("windows-1252")
        return value
    except:
        return unidecode(value)


def create(entries: List[EntryType], class_list: List[ClassInfoType]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # write header
    writer.writerow(
        [
            "OE0001_V12",
            "Entry Id",
            "Stno",
            "XStno",
            "Chipno",
            "Database Id",
            "IOF Id",
            "Surname",
            "First name",
            "Birthdate",
            "YB",
            "S",
            "Block",
            "nc",
            "Start",
            "Finish",
            "Time",
            "Classifier",
            "Credit -",
            "Penalty +",
            "Comment",
            "Club no.",
            "Cl.name",
            "City",
            "Nat",
            "Location",
            "Region",
            "Cl. no.",
            "Short",
            "Long",
            "Entry cl. No",
            "Entry class (short)",
            "Entry class (long)",
            "Rank",
            "Ranking points",
            "Num1",
            "Num2",
            "Num3",
            "Text1",
            "Text2",
            "Text3",
            "Addr. surname",
            "Addr. first name",
            "Street",
            "Line2",
            "Zip",
            "Addr. city",
            "Phone",
            "Mobile",
            "Fax",
            "EMail",
            "Rented",
            "Start fee",
            "Paid",
            "Team id",
            "Team name",
            "Course no.",
            "Course",
            "km",
            "m",
            "Course controls",
        ]
    )

    STATUS_MAP = {
        ResultStatus.INACTIVE: "",
        ResultStatus.ACTIVE: "",
        ResultStatus.FINISHED: "",
        ResultStatus.OK: "0",
        ResultStatus.MISSING_PUNCH: "3",
        ResultStatus.DID_NOT_START: "1",
        ResultStatus.DID_NOT_FINISH: "2",
        ResultStatus.OVER_TIME: "5",
        ResultStatus.DISQUALIFIED: "4",
    }

    # write entries
    for i, e in enumerate(entries):
        class_no = ""
        class_name = ""
        class_short_name = ""
        for j, c in enumerate(class_list):
            if c.id == e.class_id:
                class_no = str(j + 1)
                class_name = c.name
                if c.short_name:
                    class_short_name = c.short_name
                else:
                    class_short_name = class_name
                break

        # export only items with defined name
        if e.last_name:
            chip = e.chip if e.chip is not None else ""
            last_name = e.last_name
            first_name = e.first_name

            year = str(e.year) if e.year is not None else ""

            gender = {None: "", "": "", "F": "F", "M": "M"}[e.gender]
            not_competing = "X" if e.not_competing else "0"

            start_time = ""
            if e.result.start_time is not None:
                start_time = e.result.start_time.strftime("%H:%M:%S")

            finish_time = ""
            if e.result.finish_time is not None:
                finish_time = e.result.finish_time.strftime("%H:%M:%S")

            result_time = ""
            if e.result.time is not None:
                result_time = "{:02d}:{:02d}:{:02d}".format(
                    e.result.time // 3600,
                    e.result.time % 3600 // 60,
                    e.result.time % 60,
                )

            status = STATUS_MAP.get(e.result.status, "")

            club_id = ""
            if e.club_id is not None:
                club_id = str(e.club_id)

            club_name = ""
            if e.club_id is not None:
                club_name = e.club_name

            writer.writerow(
                [
                    "",  # OE0001_V12
                    "",  # Entry Id
                    str(i + 1),  # Stno
                    "",  # XStno
                    chip,  # Chipno
                    "",  # Database Id
                    "",  # IOF Id
                    cp1252(last_name),  # Surname
                    cp1252(first_name),  # First name
                    "",  # Birthdate
                    year,  # YB
                    gender,  # S
                    "",  # Block
                    not_competing,  # nc
                    start_time,  # Start
                    finish_time,  # Finish
                    result_time,  # Time
                    status,  # Classifier
                    "",  # Credit -
                    "",  # Penalty +
                    "",  # Comment
                    club_id,  # Club no.
                    "",  # Cl.name
                    cp1252(club_name),  # City
                    "",  # Nat
                    "",  # Location
                    "",  # Region
                    class_no,  # Cl. no.
                    class_short_name,  # Short
                    class_name,  # Long
                    "",  # Entry cl. No
                    "",  # Entry class (short)
                    "",  # Entry class (long)
                    "",  # Rank
                    "",  # Ranking points
                    "",  # Num1
                    "",  # Num2
                    "",  # Num3
                    "",  # Text1
                    "",  # Text2
                    "",  # Text3
                    "",  # Addr. surname
                    "",  # Addr. first name
                    "",  # Street
                    "",  # Line2
                    "",  # Zip
                    "",  # Addr. city
                    "",  # Phone
                    "",  # Mobile
                    "",  # Fax
                    "",  # EMail
                    "",  # Rented
                    "",  # Start fee
                    "",  # Paid
                    "",  # Team id
                    "",  # Team name
                    "",  # Course no.
                    "",  # Course
                    "",  # km
                    "",  # m
                    "",  # Course controls
                ]
            )

    content = output.getvalue()
    output.close()
    return content.encode(encoding="windows-1252")

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
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Dict

import clevercsv as csv
from unidecode import unidecode

from ooresults.repo import result_type
from ooresults.repo import start_type
from ooresults.repo.result_type import ResultStatus


def cp1252(value: str) -> str:
    try:
        _ = value.encode("windows-1252")
        return value
    except:
        return unidecode(value)


def create(entries: List[Dict], class_list: List[Dict]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # write header
    writer.writerow(
        [
            "Stnr",
            "Chip",
            "Datenbank Id",
            "Nachname",
            "Vorname",
            "Jg",
            "G",
            "Block",
            "AK",
            "Start",
            "Ziel",
            "Zeit",
            "Wertung",
            "Club-Nr.",
            "Abk",
            "Ort",
            "Nat",
            "Katnr",
            "Kurz",
            "Lang",
        ]
    )

    STATUS_MAP = {
        ResultStatus.INACTIVE: "",
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
            if c.get("id") == e.get("class_id", None):
                class_no = str(j + 1)
                class_name = c.get("name", "")
                if c.get("short_name", None):
                    class_short_name = c.get("short_name", class_name)
                else:
                    class_short_name = class_name
                break

        # export only items with defined name
        if e.get("last_name", None) is not None:
            chip = e.get("chip", "")
            last_name = e.get("last_name", "")
            first_name = e.get("first_name", "")

            year = ""
            if e.get("year", None) is not None:
                year = str(e.get("year", None))

            gender = {"": "", "F": "W", "M": "M"}[e.get("gender", "")]
            not_competing = "X" if e.get("not_competing", False) else "0"

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
            if e.get("club_id", None) is not None:
                club_id = str(e.get("club_id", None))

            club_name = ""
            if e.get("club_id", None) is not None:
                club_name = e.get("club", "")

            writer.writerow(
                [
                    str(i + 1),  # Stnr
                    chip,  # Chip
                    "",  # Datenbank Id
                    cp1252(last_name),  # Nachname
                    cp1252(first_name),  # Vorname
                    year,  # Jg
                    gender,  # G
                    "",  # Block
                    not_competing,  # AK
                    start_time,  # Start
                    finish_time,  # Ziel
                    result_time,  # Zeit
                    status,  # Wertung
                    club_id,  # Club-Nr.
                    "",  # Abk
                    cp1252(club_name),  # Ort
                    "",  # Nat
                    class_no,  # Katnr
                    class_short_name,  # Kurz
                    class_name,  # Lang
                ]
            )

    content = output.getvalue()
    output.close()
    return content.encode(encoding="windows-1252")


def parse(content: bytes) -> List[Dict]:
    column_nr = {}
    result = []

    try:
        content = content.decode(encoding="utf-8")
    except:
        content = content.decode(encoding="windows-1252")

    dialect = csv.Sniffer().sniff(content, delimiters=",;\t")
    for values in csv.reader(io.StringIO(content), dialect=dialect):
        if column_nr == {}:
            for i, v in enumerate(values):
                if v in ["Chip", "Chipno", "Chipnr", "SI card1"]:
                    column_nr["chip"] = i
                    break
            else:
                raise RuntimeError("Chip column not found")

            for i, v in enumerate(values):
                if v in ["First name", "Vorname"]:
                    column_nr["first_name"] = i
                    break
            else:
                raise RuntimeError("First name column not found")

            for i, v in enumerate(values):
                if v in ["Last name", "Nachname", "Surname"]:
                    column_nr["last_name"] = i
                    break
            else:
                raise RuntimeError("Last name column not found")

            for i, v in enumerate(values):
                if v in ["Time", "Zeit", "Time1"]:
                    column_nr["time"] = i
                    break
            else:
                raise RuntimeError("Time column not found")

            for i, v in enumerate(values):
                if v in ["Gender", "G", "S"]:
                    column_nr["gender"] = i
                    break
            else:
                raise RuntimeError("Gender column not found")

            for i, v in enumerate(values):
                if v in ["Year", "Jg", "YB"]:
                    column_nr["year"] = i
                    break
            else:
                raise RuntimeError("Year column not found")

            for i, v in enumerate(values):
                if v in ["AK", "nc"]:
                    column_nr["AK"] = i
                    break
            else:
                raise RuntimeError("AK column not found")

            for i, v in enumerate(values):
                if v in ["Result", "Wertung", "Classifier", "Classifier1"]:
                    column_nr["status"] = i
                    break
            else:
                raise RuntimeError("Result column not found")

            for i, v in enumerate(values):
                if v in ["Class", "Lang", "Long"]:
                    column_nr["class_"] = i
                    break
            else:
                raise RuntimeError("Class column not found")

            for i, v in enumerate(values):
                if v in ["City", "Ort"]:
                    column_nr["club"] = i
                    break
            else:
                raise RuntimeError("City column not found")

            for i, v in enumerate(values):
                if v in ["Cl.name", "Abk"]:
                    column_nr["club1"] = i
                    break
            else:
                raise RuntimeError("Cl.name column not found")

            for i, v in enumerate(values):
                if v in ["Start", "Start1"]:
                    column_nr["start_time"] = i
                    break
            else:
                raise RuntimeError("Start column not found")

            for i, v in enumerate(values):
                if v in ["Ziel", "Finish", "Finish1"]:
                    column_nr["finish_time"] = i
                    break
            else:
                raise RuntimeError("Finish column not found")

            for i, v in enumerate(values):
                if v in ["Text1"]:
                    column_nr["text_1"] = i
                    break

            for i, v in enumerate(values):
                if v in ["Text2"]:
                    column_nr["text_2"] = i
                    break

            for i, v in enumerate(values):
                if v in ["Text3"]:
                    column_nr["text_3"] = i
                    break

            for i, v in enumerate(values):
                if v in ["Posten1", "Control1"]:
                    column_nr["split_time"] = i
                    break
        else:
            r = {
                "start": start_type.PersonRaceStart(),
                "result": result_type.PersonRaceResult(),
            }
            fields = {}

            for column in column_nr:
                item = values[column_nr[column]]
                if column == "status":
                    mapping = {
                        "0": ResultStatus.OK,
                        "1": ResultStatus.DID_NOT_START,
                        "2": ResultStatus.DID_NOT_FINISH,
                        "3": ResultStatus.MISSING_PUNCH,
                        "4": ResultStatus.DISQUALIFIED,
                        "5": ResultStatus.OVER_TIME,
                    }
                    r["result"].status = mapping.get(item, ResultStatus.INACTIVE)
                elif column == "start_time":
                    if item != "":
                        t = 0
                        for i in item.split(":"):
                            t = 60 * t + int(i)
                        d = datetime(year=1900, month=1, day=1) + timedelta(seconds=t)
                        r["start"].start_time = d
                elif column == "finish_time":
                    if item != "":
                        t = 0
                        for i in item.split(":"):
                            t = 60 * t + int(i)
                        d = datetime(year=1900, month=1, day=1) + timedelta(seconds=t)
                        r["result"].finish_time = d
                        r["result"].punched_finish_time = d
                elif column == "time":
                    try:
                        t = 0
                        for i in item.split(":"):
                            t = 60 * t + int(i)
                        r["result"].time = t
                    except:
                        pass
                elif column == "year":
                    try:
                        if int(item) <= 25:
                            r["year"] = 2000 + int(item)
                        elif int(item) <= 99:
                            r["year"] = 1900 + int(item)
                        else:
                            r["year"] = int(item)
                    except:
                        r["year"] = None
                elif column == "gender":
                    if item == "":
                        r["gender"] = ""
                    elif item in ["f", "F", "w", "W", "d", "D"]:
                        r["gender"] = "F"
                    else:
                        r["gender"] = "M"
                elif column == "AK":
                    r["not_competing"] = item == "X"
                elif column == "text_1":
                    fields[0] = item
                elif column == "text_2":
                    fields[1] = item
                elif column == "text_3":
                    fields[2] = item
                elif column == "split_time":
                    for i in range(column_nr[column], len(values) - 1, 2):
                        # posten_1, stempelzeit_1, ..., posten_n, stempelzeit_n
                        control_code = values[i]
                        control_time = values[i + 1]
                        try:
                            t = 0
                            for j in control_time.split(":"):
                                t = 60 * t + int(j)
                        except:
                            t = None

                        r["result"].split_times.append(
                            result_type.SplitTime(
                                control_code=control_code,
                                time=t,
                                status="Missing" if control_time == "-----" else None,
                            )
                        )
                else:
                    r[column] = item

            # add extra fields
            if fields:
                r["fields"] = fields

            # correct status
            if (
                r["result"].time is None
                and r["result"].finish_time is None
                and r["result"].status == ResultStatus.OK
            ):
                r["result"].status = ResultStatus.INACTIVE

            # SportSoftware use column "club", but OOnet use column "club1"
            # In contrast to SportSoftware, OOnet does not write any gender information
            if r["gender"] == "" and r["club1"] != "":
                r["club"] = r["club1"]
            # we remove club1 key, it is not needed outside this function
            del r["club1"]

            # store start time as start punch time only if finish time is defined
            # or status is missing punch, did not finished or over time
            if r["result"].finish_time is not None or r["result"].status in [
                ResultStatus.MISSING_PUNCH,
                ResultStatus.DID_NOT_FINISH,
                ResultStatus.OVER_TIME,
            ]:
                r["result"].start_time = r["start"].start_time
                r["result"].punched_start_time = r["start"].start_time

            # do not import entries with special names
            blacklist = ("Vacant", "Vakant", "Reserve")
            if r["last_name"] not in blacklist or r["first_name"] != "":
                result.append(r)

    return result

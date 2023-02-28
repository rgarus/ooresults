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


from ooresults.repo import result_type


def parse(content: bytes):
    try:
        content = content.decode(encoding="utf-8")
    except:
        content = content.decode(encoding="windows-1252")

    # Format:
    #
    # Bahn A - Lang
    #  1  Christian Lindner                            OC Gelb                       1:07:58
    #  2  Gisela Schmidt                               Individuals/No club           1:08:02
    #     Manuela Bodental                             Individuals/No club               mp
    #
    # Bahn B - Mittel
    #  1  Hugo Peter Wolf                              Individuals/No club             28:29
    #  1  Olaf Scholz                                  OC Rot                          28:29

    results = []
    for line in content.split("\n"):
        if line != "":
            if line[0] != " ":
                class_ = line.strip()
            else:
                r = {}
                r["class_"] = class_

                a, _, b = line[4:].strip().partition("  ")
                r["first_name"], _, r["last_name"] = a.rpartition(" ")
                r["club"], _, b = b.strip().partition("  ")
                h_m_s, _, b = b.strip().partition("  ")

                MAP_STATUS = {
                    "OK": result_type.ResultStatus.OK,
                    "MP": result_type.ResultStatus.MISSING_PUNCH,
                    "DNS": result_type.ResultStatus.DID_NOT_START,
                    "DNF": result_type.ResultStatus.DID_NOT_FINISH,
                    "DISQ": result_type.ResultStatus.DISQUALIFIED,
                }
                if h_m_s.upper() in ["MP", "DNS", "DNF", "DISQ"]:
                    r["result"] = result_type.PersonRaceResult(
                        status=MAP_STATUS[h_m_s.upper()], time=None
                    )
                else:
                    t = 0
                    for i in h_m_s.split(":"):
                        t = 60 * t + int(i)
                    r["result"] = result_type.PersonRaceResult(
                        status=result_type.ResultStatus.OK, time=t
                    )

                results.append(r)

    return results

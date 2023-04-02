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


from typing import Optional

from ooresults.repo.result_type import ResultStatus


MAP_STATUS = {
    ResultStatus.INACTIVE: "",
    ResultStatus.FINISHED: "Finished",
    ResultStatus.OK: "OK",
    ResultStatus.MISSING_PUNCH: "MP",
    ResultStatus.DID_NOT_START: "DNS",
    ResultStatus.DID_NOT_FINISH: "DNF",
    ResultStatus.OVER_TIME: "OTL",
    ResultStatus.DISQUALIFIED: "DSQ",
}


EXPERIMENTAL = False


def minutes_seconds(time: Optional[int]) -> str:
    if time is None:
        return ""
    elif time >= 0:
        return "{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)
    else:
        return "-{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)


t_globals = {
    "str": str,
    "round": round,
    "ResultStatus": ResultStatus,
    "MAP_STATUS": MAP_STATUS,
    "EXPERIMENTAL": EXPERIMENTAL,
    "minutes_seconds": minutes_seconds,
}

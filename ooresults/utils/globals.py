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

from ooresults.repo.class_type import ClassParams
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.repo.start_type import PersonRaceStart
from ooresults.utils.rental_cards import format_card
from ooresults.websocket_server import streaming_status


MAP_STATUS = {
    ResultStatus.INACTIVE: "",
    ResultStatus.ACTIVE: "Started",
    ResultStatus.FINISHED: "Finished",
    ResultStatus.OK: "OK",
    ResultStatus.MISSING_PUNCH: "MP",
    ResultStatus.DID_NOT_START: "DNS",
    ResultStatus.DID_NOT_FINISH: "DNF",
    ResultStatus.OVER_TIME: "OTL",
    ResultStatus.DISQUALIFIED: "DSQ",
}

STREAMING_STATUS = {
    streaming_status.Status.SERVER_NOT_REACHABLE: "Server not reachble",
    streaming_status.Status.ACCESS_DENIED: "Access denied",
    streaming_status.Status.EVENT_NOT_FOUND: "Event not found",
    streaming_status.Status.ERROR: "Error",
    streaming_status.Status.OK: "Ok",
}

EXPERIMENTAL = False


def minutes_seconds(time: Optional[int]) -> str:
    if time is None:
        return ""
    elif time >= 0:
        return "{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)
    else:
        return "-{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)


def streaming_status_ok(status: streaming_status.Status) -> bool:
    return status == streaming_status.Status.OK


t_globals = {
    "str": str,
    "round": round,
    "ClassParams": ClassParams,
    "ResultStatus": ResultStatus,
    "SplitTime": SplitTime,
    "SpStatus": SpStatus,
    "PersonRaceResult": PersonRaceResult,
    "PersonRaceStart": PersonRaceStart,
    "MAP_STATUS": MAP_STATUS,
    "STREAMING_STATUS": STREAMING_STATUS,
    "streaming_status_ok": streaming_status_ok,
    "EXPERIMENTAL": EXPERIMENTAL,
    "minutes_seconds": minutes_seconds,
    "format_card": format_card,
}

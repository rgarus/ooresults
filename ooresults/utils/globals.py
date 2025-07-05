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


from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.entry_type import RankedEntryType
from ooresults.otypes.result_type import ResultStatus
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
    streaming_status.Status.NOT_CONNECTED: "Not connected",
    streaming_status.Status.INTERNAL_ERROR: "Internal error",
    streaming_status.Status.PROTOCOL_ERROR: "Protocol error",
    streaming_status.Status.EVENT_NOT_FOUND: "Event not found",
    streaming_status.Status.ERROR: "Error",
    streaming_status.Status.OK: "Ok",
}


def build_columns(
    class_results: List[Tuple[ClassInfoType, List[RankedEntryType]]]
) -> Set[str]:
    columns = set()
    for class_, _ in class_results:
        if class_.params.apply_handicap_rule:
            columns.add("factor")
        if class_.params.penalty_controls is not None:
            columns.add("penalties_controls")
        if class_.params.penalty_overtime is not None:
            columns.add("penalties_overtime")
        if class_.params.otype == "score":
            columns.add("score")
    return columns


def minutes_seconds(time: Optional[int]) -> str:
    if time is None:
        return ""
    elif time >= 0:
        return "{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)
    else:
        return "-{:d}:{:02d}".format(abs(time) // 60, abs(time) % 60)


def streaming_status_ok(status: streaming_status.Status) -> bool:
    return status == streaming_status.Status.OK

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


from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict

from pytest import fixture

from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus


tzinfo_1 = timezone(timedelta(hours=1))
tzinfo_4 = timezone(timedelta(hours=4))


@fixture
def c_min() -> PersonRaceResult:
    return PersonRaceResult()


@fixture
def d_min() -> Dict:
    return {
        "status": 0,
        "splitTimes": [],
        "lastLegVoided": False,
        "extensions": {},
    }


@fixture
def j_min() -> str:
    return (
        "{"
        '"status":0,'
        '"splitTimes":[],'
        '"lastLegVoided":false,'
        '"extensions":{}'
        "}"
    )


def test_min_to_dict(c_min: PersonRaceResult, d_min: Dict):
    assert c_min.to_dict() == d_min


def test_min_to_json(c_min: PersonRaceResult, j_min: str):
    assert c_min.to_json() == j_min


def test_min_from_dict(d_min: Dict, c_min: PersonRaceResult):
    assert PersonRaceResult.from_dict(d_min) == c_min


def test_min_from_json(j_min: str, c_min: PersonRaceResult):
    assert PersonRaceResult.from_json(j_min) == c_min


@fixture
def c_max() -> PersonRaceResult:
    return PersonRaceResult(
        status=ResultStatus.DID_NOT_FINISH,
        start_time=datetime(2020, 2, 9, 10, 0, 0, tzinfo=tzinfo_1),
        finish_time=datetime(2020, 2, 9, 10, 1, 1, tzinfo=tzinfo_4),
        punched_clear_time=datetime(2020, 2, 9, 10, 2, 2, tzinfo=tzinfo_1),
        punched_check_time=datetime(2020, 2, 9, 10, 3, 3, tzinfo=tzinfo_4),
        punched_start_time=datetime(2020, 2, 9, 10, 4, 4, tzinfo=tzinfo_1),
        punched_finish_time=datetime(2020, 2, 9, 10, 5, 5, tzinfo=tzinfo_4),
        si_punched_start_time=datetime(2020, 2, 9, 10, 6, 6, tzinfo=tzinfo_1),
        si_punched_finish_time=datetime(2020, 2, 9, 10, 7, 7, tzinfo=tzinfo_4),
        time=1782,
        split_times=[
            SplitTime(
                control_code="257",
                punch_time=SplitTime.NO_TIME,
                si_punch_time=datetime(2020, 2, 9, 10, 0, 0, tzinfo=tzinfo_1),
                time=34,
                status=SpStatus.ADDITIONAL,
                leg_voided=False,
            ),
            SplitTime(
                control_code="152",
                punch_time=datetime(2020, 2, 9, 10, 12, 59, tzinfo=tzinfo_1),
                si_punch_time=datetime(2020, 2, 9, 10, 13, 7, tzinfo=tzinfo_1),
                time=53,
                status=SpStatus.OK,
                leg_voided=True,
            ),
        ],
        last_leg_voided=True,
        extensions={
            "factor": 0.7546,
            "penalties_controls": 30,
            "penalties_overtime": 12,
            "running_time": 2033,
            "score_controls": 10.87,
            "score_overtime": 0.15,
            "score": 15.99,
        },
    )


@fixture
def d_max() -> Dict:
    return {
        "status": 6,
        "startTime": "2020-02-09T10:00:00+01:00",
        "finishTime": "2020-02-09T10:01:01+04:00",
        "punchedClearTime": "2020-02-09T10:02:02+01:00",
        "punchedCheckTime": "2020-02-09T10:03:03+04:00",
        "punchedStartTime": "2020-02-09T10:04:04+01:00",
        "punchedFinishTime": "2020-02-09T10:05:05+04:00",
        "siPunchedStartTime": "2020-02-09T10:06:06+01:00",
        "siPunchedFinishTime": "2020-02-09T10:07:07+04:00",
        "time": 1782,
        "splitTimes": [
            {
                "controlCode": "257",
                "punchTime": "1970-01-01T00:00:00+00:00",
                "siPunchTime": "2020-02-09T10:00:00+01:00",
                "time": 34,
                "status": 2,
                "legVoided": False,
            },
            {
                "controlCode": "152",
                "punchTime": "2020-02-09T10:12:59+01:00",
                "siPunchTime": "2020-02-09T10:13:07+01:00",
                "time": 53,
                "status": 0,
                "legVoided": True,
            },
        ],
        "lastLegVoided": True,
        "extensions": {
            "factor": 0.7546,
            "penalties_controls": 30,
            "penalties_overtime": 12,
            "running_time": 2033,
            "score_controls": 10.87,
            "score_overtime": 0.15,
            "score": 15.99,
        },
    }


@fixture
def j_max() -> str:
    return (
        "{"
        '"status":6,'
        '"startTime":"2020-02-09T10:00:00+01:00",'
        '"finishTime":"2020-02-09T10:01:01+04:00",'
        '"punchedClearTime":"2020-02-09T10:02:02+01:00",'
        '"punchedCheckTime":"2020-02-09T10:03:03+04:00",'
        '"punchedStartTime":"2020-02-09T10:04:04+01:00",'
        '"punchedFinishTime":"2020-02-09T10:05:05+04:00",'
        '"siPunchedStartTime":"2020-02-09T10:06:06+01:00",'
        '"siPunchedFinishTime":"2020-02-09T10:07:07+04:00",'
        '"time":1782,'
        '"splitTimes":['
        "{"
        '"controlCode":"257",'
        '"punchTime":"1970-01-01T00:00:00+00:00",'
        '"siPunchTime":"2020-02-09T10:00:00+01:00",'
        '"time":34,'
        '"status":2,'
        '"legVoided":false'
        "},"
        "{"
        '"controlCode":"152",'
        '"punchTime":"2020-02-09T10:12:59+01:00",'
        '"siPunchTime":"2020-02-09T10:13:07+01:00",'
        '"time":53,'
        '"status":0,'
        '"legVoided":true'
        "}"
        "],"
        '"lastLegVoided":true,'
        '"extensions":{'
        '"factor":0.7546,'
        '"penalties_controls":30,'
        '"penalties_overtime":12,'
        '"running_time":2033,'
        '"score_controls":10.87,'
        '"score_overtime":0.15,'
        '"score":15.99'
        "}"
        "}"
    )


def test_max_to_dict(c_max: PersonRaceResult, d_max: Dict):
    assert c_max.to_dict() == d_max


def test_max_to_json(c_max: PersonRaceResult, j_max: str):
    assert c_max.to_json() == j_max


def test_max_from_dict(d_max: Dict, c_max: PersonRaceResult):
    assert PersonRaceResult.from_dict(d_max) == c_max


def test_max_from_json(j_max: str, c_max: PersonRaceResult):
    assert PersonRaceResult.from_json(j_max) == c_max

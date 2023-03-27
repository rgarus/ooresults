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
from datetime import timezone

from ooresults.plugins.oe2003 import parse
from ooresults.repo import result_type
from ooresults.repo import start_type
from ooresults.repo.result_type import ResultStatus


header = [
    "Chip",
    "Vorname",
    "Nachname",
    "Start",
    "Ziel",
    "Zeit",
    "G",
    "Jg",
    "AK",
    "Wertung",
    "Lang",
    "Abk",
    "Ort",
]
tz = datetime.now(timezone.utc).astimezone().tzinfo


def test_separator_comma():
    value = "c,v,n,,,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_separator_semicolon():
    value = "c;v;n;;;;;;;;;;"
    content = bytes(";".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_separator_tab():
    value = "c\tv\tn\t\t\t\t\t\t\t\t\t\t"
    content = bytes("\t".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_quoted_data():
    value = '"c","v","n","","","","","","","","","",""'
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_quote_within_quotes():
    value = 'c,v,"n1""2",,,,,,,,,,'
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": 'n1"2',
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_separator_within_quotes():
    value = 'c,v,"n1,2",,,,,,,,,,'
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n1,2",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_newline_within_quotes():
    value = 'c,v,"n1\n2",,,,,,,,,,'
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n1\n2",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_ok_and_defined_time():
    value = "c,v,n,,,0:10,,,,0,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=10),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_ok_but_no_time():
    value = "c,v,n,,,,,,,0,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_dns():
    value = "c,v,n,,,,,,,1,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DID_NOT_START, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_dnf():
    value = "c,v,n,,,,,,,2,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DID_NOT_FINISH, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_mp():
    value = "c,v,n,,,,,,,3,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.MISSING_PUNCH, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_disq():
    value = "c,v,n,,,,,,,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_status_over_time():
    value = "c,v,n,,,,,,,5,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.OVER_TIME, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_gender_male():
    value = "c,v,n,,,,M,,,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "M",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_gender_female():
    value = "c,v,n,,,,F,,,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "F",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_club_name():
    value = "c,v,n,,,,F,,,4,,OC Red,OC Green"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "OC Green",
            "chip": "c",
            "gender": "F",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


# orienteeringonline.net uses another column for the club name,
# but in opposite to oe2003 is does not write gender data
def test_club_name_if_no_gender_is_defined():
    value = "c,v,n,,,,,,,4,,OC Red,OC Green"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "OC Red",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_year2():
    value = "c,v,n,,,,,15,,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": 2015,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_year4():
    value = "c,v,n,,,,,1915,,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": 1915,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_not_competing_is_false():
    value = "c,v,n,,,,,,0,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_not_competing_is_true():
    value = "c,v,n,,,,,,X,4,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": True,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DISQUALIFIED, time=None
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_start_time():
    value = "c,v,n,14:05:00,,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 14, 5, 0)
            ),
        }
    ]


def test_relative_start_time_h_m_s():
    value = "c,v,n,4:05:00,,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 4, 5, 0)
            ),
        }
    ]


def test_relative_start_time_m_s():
    value = "c,v,n,245:02,,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE, time=None
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 4, 5, 2)
            ),
        }
    ]


def test_finish_time():
    value = "c,v,n,,18:59:12,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                finish_time=datetime(1900, 1, 1, 18, 59, 12),
                punched_finish_time=datetime(1900, 1, 1, 18, 59, 12),
                time=None,
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_relative_finish_time_h_m_s():
    value = "c,v,n,,1:59:12,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                finish_time=datetime(1900, 1, 1, 1, 59, 12),
                punched_finish_time=datetime(1900, 1, 1, 1, 59, 12),
                time=None,
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_relative_finish_time_m_s():
    value = "c,v,n,,299:12,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                finish_time=datetime(1900, 1, 1, 4, 59, 12),
                punched_finish_time=datetime(1900, 1, 1, 4, 59, 12),
                time=None,
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_start_and_finish_time():
    value = "c,v,n,14:05:00,14:36:11,,,,,,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                start_time=datetime(1900, 1, 1, 14, 5, 0),
                punched_start_time=datetime(1900, 1, 1, 14, 5, 0),
                finish_time=datetime(1900, 1, 1, 14, 36, 11),
                punched_finish_time=datetime(1900, 1, 1, 14, 36, 11),
                time=None,
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 14, 5, 0)
            ),
        }
    ]


def test_start_time_and_status_mp():
    value = "c,v,n,14:05:00,,,,,,3,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.MISSING_PUNCH,
                start_time=datetime(1900, 1, 1, 14, 5, 0),
                punched_start_time=datetime(1900, 1, 1, 14, 5, 0),
                time=None,
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 14, 5, 0)
            ),
        }
    ]


def test_start_time_and_status_dnf():
    value = "c,v,n,14:05:00,,,,,,2,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.DID_NOT_FINISH,
                start_time=datetime(1900, 1, 1, 14, 5, 0),
                punched_start_time=datetime(1900, 1, 1, 14, 5, 0),
                time=None,
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 14, 5, 0)
            ),
        }
    ]


def test_start_time_and_status_over_time():
    value = "c,v,n,14:05:00,,,,,,5,,,"
    content = bytes(",".join(header) + "\n" + value, encoding="utf-8")
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.OVER_TIME,
                start_time=datetime(1900, 1, 1, 14, 5, 0),
                punched_start_time=datetime(1900, 1, 1, 14, 5, 0),
                time=None,
            ),
            "start": start_type.PersonRaceStart(
                start_time=datetime(1900, 1, 1, 14, 5, 0)
            ),
        }
    ]


def test_split_time():
    value = "c,v,n,,,,,,,,,,,123,4:16"
    content = bytes(
        ",".join(header + ["Posten1,Punch1"]) + "\n" + value, encoding="utf-8"
    )
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                split_times=[
                    result_type.SplitTime(control_code="123", time=256, status=None),
                ],
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_split_time_without_punch():
    value = "c,v,n,,,,,,,,,,,123,-----"
    content = bytes(
        ",".join(header + ["Posten1,Punch1"]) + "\n" + value, encoding="utf-8"
    )
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                split_times=[
                    result_type.SplitTime(
                        control_code="123", time=None, status="Missing"
                    ),
                ],
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_two_split_times():
    value = "c,v,n,,,,,,,,,,,123,4:16,99,12:01"
    content = bytes(
        ",".join(header + ["Posten1,Punch1"]) + "\n" + value, encoding="utf-8"
    )
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                split_times=[
                    result_type.SplitTime(control_code="123", time=256, status=None),
                    result_type.SplitTime(control_code="99", time=721, status=None),
                ],
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_split_times_with_closing_separator():
    value = "c,v,n,,,,,,,,,,,123,4:16,99,12:01,"
    content = bytes(
        ",".join(header + ["Posten1,Punch1"]) + "\n" + value, encoding="utf-8"
    )
    assert parse(content) == [
        {
            "first_name": "v",
            "last_name": "n",
            "class_": "",
            "club": "",
            "chip": "c",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(
                status=ResultStatus.INACTIVE,
                split_times=[
                    result_type.SplitTime(control_code="123", time=256, status=None),
                    result_type.SplitTime(control_code="99", time=721, status=None),
                ],
            ),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_import_several_lines():
    value_1 = "c1,v1,n1,,,0:11,,,,0,,,"
    value_2 = "c2,v2,n2,,,0:12,,,,0,,,"
    value_3 = "c3,v3,n3,,,0:13,,,,0,,,"
    content = bytes(
        ",".join(header) + "\n" + value_1 + "\n" + value_2 + "\n" + value_3,
        encoding="utf-8",
    )
    assert parse(content) == [
        {
            "first_name": "v1",
            "last_name": "n1",
            "class_": "",
            "club": "",
            "chip": "c1",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=11),
            "start": start_type.PersonRaceStart(),
        },
        {
            "first_name": "v2",
            "last_name": "n2",
            "class_": "",
            "club": "",
            "chip": "c2",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=12),
            "start": start_type.PersonRaceStart(),
        },
        {
            "first_name": "v3",
            "last_name": "n3",
            "class_": "",
            "club": "",
            "chip": "c3",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=13),
            "start": start_type.PersonRaceStart(),
        },
    ]


def test_do_not_import_special_names():
    value_1 = "c1,,Vacant,,,0:11,,,,0,,,"
    value_2 = "c2,v2,n2,,,0:12,,,,0,,,"
    value_3 = "c3,,Reserve,,,0:13,,,,0,,,"
    content = bytes(
        ",".join(header) + "\n" + value_1 + "\n" + value_2 + "\n" + value_3,
        encoding="utf-8",
    )
    assert parse(content) == [
        {
            "first_name": "v2",
            "last_name": "n2",
            "class_": "",
            "club": "",
            "chip": "c2",
            "gender": "",
            "year": None,
            "not_competing": False,
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=12),
            "start": start_type.PersonRaceStart(),
        }
    ]


def test_import_extra_fields():
    value_1 = "c1,v1,n1,,,0:11,,,,0,,,,A,B,C"
    value_2 = "c2,v2,n2,,,0:12,,,,0,,,,,X,"
    value_3 = "c3,v3,n3,,,0:13,,,,0,,,,,Y,Z"
    content = bytes(
        ",".join(header + ["Text1", "Text2", "Text3"])
        + "\n"
        + value_1
        + "\n"
        + value_2
        + "\n"
        + value_3,
        encoding="utf-8",
    )
    assert parse(content) == [
        {
            "first_name": "v1",
            "last_name": "n1",
            "class_": "",
            "club": "",
            "chip": "c1",
            "gender": "",
            "year": None,
            "not_competing": False,
            "fields": {0: "A", 1: "B", 2: "C"},
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=11),
            "start": start_type.PersonRaceStart(),
        },
        {
            "first_name": "v2",
            "last_name": "n2",
            "class_": "",
            "club": "",
            "chip": "c2",
            "gender": "",
            "year": None,
            "not_competing": False,
            "fields": {0: "", 1: "X", 2: ""},
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=12),
            "start": start_type.PersonRaceStart(),
        },
        {
            "first_name": "v3",
            "last_name": "n3",
            "class_": "",
            "club": "",
            "chip": "c3",
            "gender": "",
            "year": None,
            "not_competing": False,
            "fields": {0: "", 1: "Y", 2: "Z"},
            "result": result_type.PersonRaceResult(status=ResultStatus.OK, time=13),
            "start": start_type.PersonRaceStart(),
        },
    ]

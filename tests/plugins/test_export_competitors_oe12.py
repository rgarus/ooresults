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


import datetime

from ooresults.plugins import oe12
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus


header = (
    "OE0001_V12;"
    "Entry Id;"
    "Stno;"
    "XStno;"
    "Chipno;"
    "Database Id;"
    "IOF Id;"
    "Surname;"
    "First name;"
    "Birthdate;"
    "YB;"
    "S;"
    "Block;"
    "nc;"
    "Start;"
    "Finish;"
    "Time;"
    "Classifier;"
    "Credit -;"
    "Penalty +;"
    "Comment;"
    "Club no.;"
    "Cl.name;"
    "City;"
    "Nat;"
    "Location;"
    "Region;"
    "Cl. no.;"
    "Short;"
    "Long;"
    "Entry cl. No;"
    "Entry class (short);"
    "Entry class (long);"
    "Rank;"
    "Ranking points;"
    "Num1;"
    "Num2;"
    "Num3;"
    "Text1;"
    "Text2;"
    "Text3;"
    "Addr. surname;"
    "Addr. first name;"
    "Street;"
    "Line2;"
    "Zip;"
    "Addr. city;"
    "Phone;"
    "Mobile;"
    "Fax;"
    "EMail;"
    "Rented;"
    "Start fee;"
    "Paid;"
    "Team id;"
    "Team name;"
    "Course no.;"
    "Course;"
    "km;"
    "m;"
    "Course controls"
)
encoding = "windows-1252"


def test_separator_semicolon():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v",
                last_name="n",
                chip="c",
            ),
        ],
        class_list=[],
    )
    v1 = ";;1;;c;;;n;v;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

    assert content == bytes(header + "\r\n" + v1 + "\r\n", encoding=encoding)


def test_quote_within_quotes():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v",
                last_name='n1"2',
                chip="c",
            ),
        ],
        class_list=[],
    )
    v1 = ';;1;;c;;;"n1""2";v;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'

    assert content == bytes(header + "\r\n" + v1 + "\r\n", encoding=encoding)


def test_separator_within_quotes():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v",
                last_name="n1;2",
                chip="c",
            ),
        ],
        class_list=[],
    )
    v1 = ';;1;;c;;;"n1;2";v;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'

    assert content == bytes(header + "\r\n" + v1 + "\r\n", encoding=encoding)


def test_newline_within_quotes():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v",
                last_name="n1\n2",
                chip="c",
            ),
        ],
        class_list=[],
    )
    v1 = ';;1;;c;;;"n1\n2";v;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'

    assert content == bytes(header + "\r\n" + v1 + "\r\n", encoding=encoding)


def test_special_characters():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v",
                last_name="ÄÖÜßäüö",
                chip="c",
            ),
        ],
        class_list=[],
    )
    v1 = ";;1;;c;;;ÄÖÜßäüö;v;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

    assert content == bytes(header + "\r\n" + v1 + "\r\n", encoding=encoding)


def test_multiline():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="v1",
                last_name="n1",
                chip="c1",
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="v2",
                last_name="n2",
                chip="c2",
            ),
            EntryType(
                id=3,
                event_id=1,
                competitor_id=3,
                first_name="v3",
                last_name="n3",
                chip="c3",
            ),
        ],
        class_list=[],
    )
    v1 = ";;1;;c1;;;n1;v1;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    v2 = ";;2;;c2;;;n2;v2;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    v3 = ";;3;;c3;;;n3;v3;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

    assert content == bytes(
        header + "\r\n" + v1 + "\r\n" + v2 + "\r\n" + v3 + "\r\n", encoding=encoding
    )


def test_year():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                year=2006,
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                year=2000,
            ),
            EntryType(
                id=3,
                event_id=1,
                competitor_id=3,
                first_name="e",
                last_name="f",
                year=1941,
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;2006;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;2000;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;3;;;;;f;e;;1941;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_gender():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                gender="F",
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                gender="M",
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;F;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;M;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_not_competing():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                not_competing=False,
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                not_competing=True,
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;X;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_club():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                club_id=1,
                club_name="OL1",
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                club_id=2,
                club_name="OL2",
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;;;;;1;;OL1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;;;;;2;;OL2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_club_not_exported_without_club_id():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                club_id=None,
                club_name="OL1",
            ),
            EntryType(
                id=2,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                club_id=2,
                club_name="OL2",
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;;;;;2;;OL2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_class():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                class_id=1,
                class_name="Class_1",
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                class_id=2,
                class_name="Class_2",
            ),
        ],
        class_list=[
            ClassInfoType(
                id=1,
                name="Class_1",
                short_name=None,
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=2,
                name="Class_2",
                short_name=None,
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
        ],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;;;;;;;;;;;1;Class_1;Class_1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;;;;;;;;;;;2;Class_2;Class_2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_class_short_name():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                class_id=1,
                class_name="Class_1",
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                class_id=2,
                class_name="Class_2",
            ),
        ],
        class_list=[
            ClassInfoType(
                id=1,
                name="Class_1",
                short_name="C1",
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
            ClassInfoType(
                id=2,
                name="Class_2",
                short_name="C2",
                course_id=None,
                course_name=None,
                course_length=None,
                course_climb=None,
                number_of_controls=None,
                params=ClassParams(),
            ),
        ],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;;;;;;;;;;;1;C1;Class_1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;;;;;;;;;;;2;C2;Class_2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_start_time():
    s1 = datetime.datetime(
        2020, 2, 9, 10, 0, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    s2 = datetime.datetime(
        2020, 3, 1, 22, 50, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(start_time=s1),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(start_time=s2),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;10:00:15;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;22:50:00;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_finish_time():
    f1 = datetime.datetime(
        2020, 2, 9, 10, 0, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    f2 = datetime.datetime(
        2020, 3, 1, 22, 50, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(finish_time=f1),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(finish_time=f2),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;10:00:15;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;22:50:00;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_time():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(time=301),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(time=8000),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;00:05:01;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;02:13:20;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_ok():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.OK),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.OK),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_dns():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.DID_NOT_START),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_dnf():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.DID_NOT_FINISH),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.DID_NOT_FINISH),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_mp():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.MISSING_PUNCH),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.MISSING_PUNCH),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;3;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;3;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_disq():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.DISQUALIFIED),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.DISQUALIFIED),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;4;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;4;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_otl():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="a",
                last_name="b",
                result=PersonRaceResult(status=ResultStatus.OVER_TIME),
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="c",
                last_name="d",
                result=PersonRaceResult(status=ResultStatus.OVER_TIME),
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;b;a;;;;;0;;;;5;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;d;c;;;;;0;;;;5;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding=encoding)


def test_status_diacritic_characters_cp1252_encoding():
    content = oe12.create(
        entries=[
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="Núria",
                last_name="Pavić",
                club_id=1,
                club_name="OC Kovač",
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=2,
                first_name="Núria Istenič",
                last_name="Müller",
                club_id=2,
                club_name="Futó Club",
            ),
            EntryType(
                id=1,
                event_id=1,
                competitor_id=1,
                first_name="Pattantyús",
                last_name="Hugo",
                club_id=3,
                club_name="OC Ábrahám",
            ),
        ],
        class_list=[],
    )
    v1 = (
        ";;1;;;;;Pavic;Núria;;;;;0;;;;;;;;1;;OC Kovac;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;2;;;;;Müller;Nuria Istenic;;;;;0;;;;;;;;2;;Futó Club;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
        ";;3;;;;;Hugo;Pattantyús;;;;;0;;;;;;;;3;;OC Ábrahám;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        "\r\n"
    )

    assert content == bytes(header + "\r\n" + v1, encoding="windows-1252")

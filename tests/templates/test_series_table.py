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
from decimal import Decimal

import pytest
from lxml import etree

from ooresults.otypes.event_type import EventType
from ooresults.otypes.series_type import PersonSeriesResult
from ooresults.otypes.series_type import Points
from ooresults.utils import render


@pytest.fixture()
def events() -> list[EventType]:
    return [
        EventType(
            id=5,
            name="1. O-Cup 2023 (Ostpark)",
            date=datetime.date(2023, 1, 15),
            key=None,
            publish=False,
            series="Lauf 1",
            fields=[],
        ),
        EventType(
            id=6,
            name="2. O-Cup 2023 (Nordpark)",
            date=datetime.date(2023, 1, 22),
            key=None,
            publish=False,
            series="Lauf 2",
            fields=[],
        ),
        EventType(
            id=7,
            name="3. O-Cup 2023 (Westpark)",
            date=datetime.date(2023, 1, 29),
            key=None,
            publish=False,
            series="Lauf 3",
            fields=[],
        ),
    ]


@pytest.fixture()
def results() -> list[tuple[str, list[PersonSeriesResult]]]:
    return [
        (
            "Bahn A - Frauen",
            [
                PersonSeriesResult(
                    last_name="Baerbock",
                    first_name="Annalena",
                    year=1980,
                    club_name="OC Grün",
                    races={
                        0: Points(points=Decimal("100.00"), bonus=False),
                        1: Points(points=Decimal("100.00"), bonus=False),
                        2: Points(points=Decimal("100.00"), bonus=False),
                    },
                    total_points=Decimal("300.00"),
                    rank=1,
                ),
                PersonSeriesResult(
                    last_name="Faeser",
                    first_name="Nancy",
                    year=1970,
                    club_name="OC Rot",
                    races={
                        0: Points(points=Decimal("49.89"), bonus=False),
                        2: Points(points=Decimal("46.53"), bonus=False),
                        1: Points(points=Decimal("48.21"), bonus=True),
                    },
                    total_points=Decimal("144.63"),
                    rank=2,
                ),
            ],
        ),
        (
            "Bahn A - Männer",
            [
                PersonSeriesResult(
                    last_name="Scholz",
                    first_name="Olaf",
                    year=1958,
                    club_name="OC Rot",
                    races={
                        0: Points(points=Decimal("82.49"), bonus=False),
                        2: Points(points=Decimal("86.52"), bonus=False),
                        1: Points(points=Decimal("84.50"), bonus=True),
                    },
                    total_points=Decimal("253.51"),
                    rank=1,
                ),
                PersonSeriesResult(
                    last_name="Buschmann",
                    first_name="Marco",
                    year=1977,
                    club_name="OC Gelb",
                    races={
                        0: Points(points=Decimal("76.29"), bonus=False),
                        1: Points(points=Decimal("87.05"), bonus=False),
                        2: Points(points=Decimal("73.99"), bonus=False),
                    },
                    total_points=Decimal("237.33"),
                    rank=2,
                ),
                PersonSeriesResult(
                    last_name="Lindner",
                    first_name="Christian",
                    year=1979,
                    club_name="OC Gelb",
                    races={
                        0: Points(points=Decimal("100.00"), bonus=False),
                        1: Points(points=Decimal("100.00"), bonus=False),
                    },
                    total_points=Decimal("200.00"),
                    rank=3,
                ),
                PersonSeriesResult(
                    last_name="Habeck",
                    first_name="Robert",
                    year=1969,
                    club_name="OC Grün",
                    races={
                        0: Points(points=Decimal("0.00"), bonus=False),
                        1: Points(points=Decimal("95.41"), bonus=False),
                        2: Points(points=Decimal("100.00"), bonus=False),
                    },
                    total_points=Decimal("195.41"),
                    rank=4,
                ),
            ],
        ),
    ]


def test_series_results(
    events: list[EventType],
    results: list[tuple[str, list[PersonSeriesResult]]],
):
    html = etree.HTML(render.series_table(events=events, results=results))

    table = html.find(".//table")
    assert [child.tag for child in table] == ["thead", "tbody", "thead", "tbody"]

    # headers
    headers = table.findall("./thead[1]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Bahn A - Frauen"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == [
        "Rank",
        "Name",
        "Club",
        "Points",
        "Lauf 1",
        "Lauf 2",
        "Lauf 3",
    ]

    # rows
    rows = table.findall("./tbody[1]/tr")
    assert len(rows) == 2

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        "1",
        "Annalena Baerbock",
        "OC Grün",
        "300.00",
        "100.00",
        "100.00",
        "100.00",
    ]

    # row 2
    assert [td.text for td in rows[1].findall(".//td")] == [
        "2",
        "Nancy Faeser",
        "OC Rot",
        "144.63",
        "49.89",
        "(48.21)",
        "46.53",
    ]

    # headers
    headers = table.findall("./thead[2]/tr")
    assert len(headers) == 2

    # header 1
    assert len(headers[0].findall(".//th")) == 1
    assert headers[0].find(".//th[1]/h3").text == "Bahn A - Männer"

    # header 2
    assert [td.text for td in headers[1].findall(".//th")] == [
        "Rank",
        "Name",
        "Club",
        "Points",
        "Lauf 1",
        "Lauf 2",
        "Lauf 3",
    ]

    # rows
    rows = table.findall("./tbody[2]/tr")
    assert len(rows) == 4

    # row 1
    assert [td.text for td in rows[0].findall(".//td")] == [
        "1",
        "Olaf Scholz",
        "OC Rot",
        "253.51",
        "82.49",
        "(84.50)",
        "86.52",
    ]

    # row 2
    assert [td.text for td in rows[1].findall(".//td")] == [
        "2",
        "Marco Buschmann",
        "OC Gelb",
        "237.33",
        "76.29",
        "87.05",
        "73.99",
    ]

    # row 3
    assert [td.text for td in rows[2].findall(".//td")] == [
        "3",
        "Christian Lindner",
        "OC Gelb",
        "200.00",
        "100.00",
        "100.00",
        None,
    ]

    # row 4
    assert [td.text for td in rows[3].findall(".//td")] == [
        "4",
        "Robert Habeck",
        "OC Grün",
        "195.41",
        "0.00",
        "95.41",
        "100.00",
    ]

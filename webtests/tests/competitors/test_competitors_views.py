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


import pathlib

import pytest

from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.table import RowIterator


@pytest.fixture(scope="module")
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture(scope="module")
def competitor_data(main_page: MainPage) -> None:
    competitor_list_path = (
        pathlib.Path(__file__).parent.parent / "data" / "CompetitorList.xml"
    )

    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.import_()
    dialog.import_file(path=competitor_list_path)


def test_if_view_is_competitors_then_group_by_competitors_sorted_by_name(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    competitor_page.view().select_by_text(text="Competitors")

    assert competitor_page.table.headers() == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]

    rows = iter(RowIterator(table=competitor_page.table))
    assert next(rows) == [
        "Competitors  (6)",
    ]
    assert next(rows) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
    ]
    assert next(rows) == [
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "OC Gelb",
    ]
    assert next(rows) == [
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "OC Rot",
    ]
    assert next(rows) == [
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
    ]
    assert next(rows) == [
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
    ]
    assert next(rows) == [
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_clubs_then_group_by_clubs_sorted_by_name(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    competitor_page.view().select_by_text(text="Clubs")

    assert competitor_page.table.headers() == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
    ]

    rows = iter(RowIterator(table=competitor_page.table))
    assert next(rows) == [
        "OC Gelb  (2)",
    ]
    assert next(rows) == [
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
    ]
    assert next(rows) == [
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
    ]
    assert next(rows) == [
        "OC Grün  (2)",
    ]
    assert next(rows) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
    ]
    assert next(rows) == [
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
    ]
    assert next(rows) == [
        "OC Rot  (2)",
    ]
    assert next(rows) == [
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
    ]
    assert next(rows) == [
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
    ]
    with pytest.raises(StopIteration):
        next(rows)

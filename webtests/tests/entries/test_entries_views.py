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
from collections.abc import Iterator

import pytest

from webtests.pageobjects.entries import ImportEntryDialog
from webtests.pageobjects.main_page import MainPage
from webtests.pageobjects.table import RowIterator


EVENT_NAME = "Test for Entries"
EVENT_DATE = "2023-01-23"


@pytest.fixture(scope="module")
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture(scope="module")
def event(main_page: MainPage, delete_all: None) -> Iterator[str]:
    event_page = main_page.goto_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE)
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


@pytest.fixture(scope="module")
def result_data(main_page: MainPage, event: str) -> None:
    result_list_path = pathlib.Path(__file__).parent.parent / "data" / "ResultList.xml"

    entry_page = main_page.goto_entries(event=event)
    dialog = entry_page.actions.import_()
    dialog.format().select(text=ImportEntryDialog.RESULT_LIST)
    assert dialog.format().selected() == ImportEntryDialog.RESULT_LIST
    dialog.import_file(path=result_list_path)


def test_if_view_is_entries_then_group_by_entries_sorted_by_name(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="Entries")

    assert entry_page.table.headers() == [
        "Rank",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start time",
        "Run time",
        "Status",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "Entries  (6)",
    ]
    assert next(rows) == [
        "(1)",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
        "Bahn A - Frauen",
        "10:10:00",
        "14:39",
        "OK",
    ]
    assert next(rows) == [
        "(3)",
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "OC Gelb",
        "Bahn A - Männer",
        "10:16:03",
        "17:30",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "OC Rot",
        "Bahn A - Frauen",
        "10:18:00",
        "29:22",
        "OK",
    ]
    assert next(rows) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
        "Bahn A - Männer",
        "10:12:00",
        "14:04",
        "MP",
    ]
    assert next(rows) == [
        "(1)",
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
        "Bahn A - Männer",
        "10:14:02",
        "13:21",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
        "Bahn A - Männer",
        "10:20:01",
        "16:11",
        "OK",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_classes_then_group_by_classes_sorted_by_name(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="Classes")

    assert entry_page.table.headers() == [
        "Rank",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Start time",
        "Run time",
        "Status",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "Bahn A - Frauen  (2)",
    ]
    assert next(rows) == [
        "(1)",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
        "10:10:00",
        "14:39",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "OC Rot",
        "10:18:00",
        "29:22",
        "OK",
    ]
    assert next(rows) == [
        "Bahn A - Männer  (4)",
    ]
    assert next(rows) == [
        "(3)",
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "OC Gelb",
        "10:16:03",
        "17:30",
        "OK",
    ]
    assert next(rows) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
        "10:12:00",
        "14:04",
        "MP",
    ]
    assert next(rows) == [
        "(1)",
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
        "10:14:02",
        "13:21",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
        "10:20:01",
        "16:11",
        "OK",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_clubs_then_group_by_clubs_sorted_by_name(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="Clubs")

    assert entry_page.table.headers() == [
        "Rank",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Class",
        "Start time",
        "Run time",
        "Status",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "OC Gelb  (2)",
    ]
    assert next(rows) == [
        "(3)",
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "Bahn A - Männer",
        "10:16:03",
        "17:30",
        "OK",
    ]
    assert next(rows) == [
        "(1)",
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "Bahn A - Männer",
        "10:14:02",
        "13:21",
        "OK",
    ]
    assert next(rows) == [
        "OC Grün  (2)",
    ]
    assert next(rows) == [
        "(1)",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "Bahn A - Frauen",
        "10:10:00",
        "14:39",
        "OK",
    ]
    assert next(rows) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "Bahn A - Männer",
        "10:12:00",
        "14:04",
        "MP",
    ]
    assert next(rows) == [
        "OC Rot  (2)",
    ]
    assert next(rows) == [
        "(2)",
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "Bahn A - Frauen",
        "10:18:00",
        "29:22",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "Bahn A - Männer",
        "10:20:01",
        "16:11",
        "OK",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_results_then_group_by_classes_sorted_by_rank(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="Results")

    assert entry_page.table.headers() == [
        "Rank",
        "Name",
        "Year",
        "Chip",
        "Club",
        "Run time",
        "Total time",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "Bahn A - Frauen  (2)",
    ]
    assert next(rows) == [
        "1",
        "Baerbock, Annalena",
        "1980",
        "7379879",
        "OC Grün",
        "",
        "14:39",
    ]
    assert next(rows) == [
        "2",
        "Faeser, Nancy",
        "1970",
        "7040504",
        "OC Rot",
        "",
        "29:22",
    ]
    assert next(rows) == [
        "Bahn A - Männer  (4)",
    ]
    assert next(rows) == [
        "1",
        "Lindner, Christian",
        "1979",
        "12345",
        "OC Gelb",
        "",
        "13:21",
    ]
    assert next(rows) == [
        "2",
        "Scholz, Olaf",
        "1958",
        "7579050",
        "OC Rot",
        "",
        "16:11",
    ]
    assert next(rows) == [
        "3",
        "Buschmann, Marco",
        "1977",
        "7076815",
        "OC Gelb",
        "",
        "17:30",
    ]
    assert next(rows) == [
        "",
        "Habeck, Robert",
        "1969",
        "7509749",
        "OC Grün",
        "",
        "MP",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_states_then_group_by_states_sorted_by_name(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="States")

    assert entry_page.table.headers() == [
        "Rank",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start time",
        "Run time",
        "Status",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "OK  (5)",
    ]
    assert next(rows) == [
        "(1)",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
        "Bahn A - Frauen",
        "10:10:00",
        "14:39",
        "OK",
    ]
    assert next(rows) == [
        "(3)",
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "OC Gelb",
        "Bahn A - Männer",
        "10:16:03",
        "17:30",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "OC Rot",
        "Bahn A - Frauen",
        "10:18:00",
        "29:22",
        "OK",
    ]
    assert next(rows) == [
        "(1)",
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
        "Bahn A - Männer",
        "10:14:02",
        "13:21",
        "OK",
    ]
    assert next(rows) == [
        "(2)",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
        "Bahn A - Männer",
        "10:20:01",
        "16:11",
        "OK",
    ]
    assert next(rows) == [
        "Missing punch  (1)",
    ]
    assert next(rows) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
        "Bahn A - Männer",
        "10:12:00",
        "14:04",
        "MP",
    ]
    with pytest.raises(StopIteration):
        next(rows)


def test_if_view_is_competitors_then_group_by_competitors_sorted_by_name(
    main_page: MainPage, event: str, result_data: None
) -> None:
    entry_page = main_page.goto_entries(event=event)
    entry_page.view().select_by_text(text="Competitors")

    assert entry_page.table.headers() == [
        "Rank",
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
        "Class",
        "Start time",
        "Run time",
        "Status",
    ]

    rows = iter(RowIterator(table=entry_page.table))
    assert next(rows) == [
        "Baerbock, Annalena  (1)",
    ]
    assert next(rows) == [
        "(1)",
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "OC Grün",
        "Bahn A - Frauen",
        "10:10:00",
        "14:39",
        "OK",
    ]
    assert next(rows) == [
        "Buschmann, Marco  (1)",
    ]
    assert next(rows) == [
        "(3)",
        "Marco",
        "Buschmann",
        "M",
        "1977",
        "7076815",
        "OC Gelb",
        "Bahn A - Männer",
        "10:16:03",
        "17:30",
        "OK",
    ]
    assert next(rows) == [
        "Faeser, Nancy  (1)",
    ]
    assert next(rows) == [
        "(2)",
        "Nancy",
        "Faeser",
        "F",
        "1970",
        "7040504",
        "OC Rot",
        "Bahn A - Frauen",
        "10:18:00",
        "29:22",
        "OK",
    ]
    assert next(rows) == [
        "Habeck, Robert  (1)",
    ]
    assert next(rows) == [
        "",
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
        "Bahn A - Männer",
        "10:12:00",
        "14:04",
        "MP",
    ]
    assert next(rows) == [
        "Lindner, Christian  (1)",
    ]
    assert next(rows) == [
        "(1)",
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
        "Bahn A - Männer",
        "10:14:02",
        "13:21",
        "OK",
    ]
    assert next(rows) == [
        "Scholz, Olaf  (1)",
    ]
    assert next(rows) == [
        "(2)",
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
        "Bahn A - Männer",
        "10:20:01",
        "16:11",
        "OK",
    ]
    with pytest.raises(StopIteration):
        next(rows)

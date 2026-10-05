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


@pytest.fixture(scope="session")
def delete_all(main_page: MainPage) -> None:
    main_page.goto_events().delete_events()
    main_page.goto_competitors().delete_competitors()
    main_page.goto_clubs().delete_clubs()


@pytest.fixture
def competitor_data(main_page: MainPage, delete_all: None) -> None:
    competitor_list_path = (
        pathlib.Path(__file__).parent.parent / "data" / "CompetitorList.xml"
    )

    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.import_()
    dialog.import_file(path=competitor_list_path)


def test_if_no_competitor_is_selected_then_both_competitors_of_the_merge_dialog_are_empty(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    assert competitor_page.table.selected_row() is None

    merge_dialog = competitor_page.actions.merge()
    merge_dialog.check_competitor_1(
        first_name="",
        last_name="",
        sex="",
        year="",
        chip="",
        club="",
    )
    merge_dialog.check_competitor_2(
        first_name="",
        last_name="",
        sex="",
        year="",
        chip="",
        club="",
    )
    assert not merge_dialog.merge_1to2_is_enabled()
    assert not merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


def test_if_a_competitor_is_selected_then_their_details_are_displayed_in_the_merge_dialog_as_first_competitor(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    competitor_page.select_competitor(first_name="Robert", last_name="Habeck")

    merge_dialog = competitor_page.actions.merge()
    merge_dialog.check_competitor_1(
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
    )
    merge_dialog.check_competitor_2(
        first_name="",
        last_name="",
        sex="",
        year="",
        chip="",
        club="",
    )
    assert not merge_dialog.merge_1to2_is_enabled()
    assert not merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


@pytest.mark.parametrize("nr", [1, 2])
def test_if_the_choose_dialog_is_opened_then_a_competitor_can_be_selected(
    nr: int, main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    merge_dialog = competitor_page.actions.merge()

    match nr:
        case 1:
            select_dialog = merge_dialog.choose_1()
        case 2:
            select_dialog = merge_dialog.choose_2()
        case _:
            raise RuntimeError(f"Unknown nr {nr}")

    assert select_dialog.table.headers() == [
        "First name",
        "Last name",
        "Sex",
        "Year",
        "Chip",
        "Club",
    ]

    rows = iter(RowIterator(table=select_dialog.table))
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

    select_dialog.cancel()
    merge_dialog.cancel()


def test_if_competitor_1_is_choosen_then_their_details_are_displayed_in_the_merge_dialog(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    competitor_page.select_competitor(first_name="Robert", last_name="Habeck")
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_1()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()

    merge_dialog.check_competitor_1(
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
    )
    merge_dialog.check_competitor_2(
        first_name="",
        last_name="",
        sex="",
        year="",
        chip="",
        club="",
    )
    assert not merge_dialog.merge_1to2_is_enabled()
    assert not merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


def test_if_competitor_2_is_choosen_then_their_details_are_displayed_in_the_merge_dialog(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    assert competitor_page.table.selected_row() is None
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_2()
    select_dialog.filter().set_text(text="Lindner")

    rows = iter(RowIterator(table=select_dialog.table))
    assert next(rows) == [
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
    ]
    with pytest.raises(StopIteration):
        next(rows)
    select_dialog.double_click_row(i=1)

    merge_dialog.check_competitor_1(
        "",
        "",
        "",
        "",
        "",
        "",
    )
    merge_dialog.check_competitor_2(
        "Christian",
        "Lindner",
        "M",
        "1979",
        "12345",
        "OC Gelb",
    )
    assert not merge_dialog.merge_1to2_is_enabled()
    assert not merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


def test_if_the_same_competitor_is_choosen_for_1_and_2_then_merge_buttons_are_disabled(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_1()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()
    select_dialog = merge_dialog.choose_2()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()

    merge_dialog.check_competitor_1(
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
    )
    merge_dialog.check_competitor_2(
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
    )
    assert not merge_dialog.merge_1to2_is_enabled()
    assert not merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


def test_if_different_competitors_are_choosen_for_1_and_2_then_merge_buttons_are_enabled(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_1()
    select_dialog.select_competitor(first_name="Robert", last_name="Habeck")
    select_dialog.save()
    select_dialog = merge_dialog.choose_2()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()

    merge_dialog.check_competitor_1(
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "OC Grün",
    )
    merge_dialog.check_competitor_2(
        "Olaf",
        "Scholz",
        "M",
        "1958",
        "7579050",
        "OC Rot",
    )
    assert merge_dialog.merge_1to2_is_enabled()
    assert merge_dialog.merge_2to1_is_enabled()
    merge_dialog.cancel()


def test_if_merging_a_competitor_is_cancelled_then_no_competitor_is_deleted(
    main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_1()
    select_dialog.select_competitor(first_name="Robert", last_name="Habeck")
    select_dialog.save()
    select_dialog = merge_dialog.choose_2()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()
    assert_dialog = merge_dialog.merge_1to2()
    assert_dialog.cancel()
    merge_dialog.cancel()

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


@pytest.mark.parametrize("direction", ["1to2", "2to1"])
def test_if_a_competitor_is_merged_then_the_competitor_is_deleted(
    direction: str, main_page: MainPage, competitor_data: None
) -> None:
    competitor_page = main_page.goto_competitors()
    merge_dialog = competitor_page.actions.merge()
    select_dialog = merge_dialog.choose_1()
    select_dialog.select_competitor(first_name="Robert", last_name="Habeck")
    select_dialog.save()
    select_dialog = merge_dialog.choose_2()
    select_dialog.select_competitor(first_name="Olaf", last_name="Scholz")
    select_dialog.save()

    match direction:
        case "1to2":
            assert_dialog = merge_dialog.merge_1to2()
            assert assert_dialog.text() == (
                "Should the competitor Robert Habeck be removed, "
                "and every instance of that name (including sex and year of birth) "
                "in all events be replaced with competitor Olaf Scholz?"
            )
            assert_dialog.ok()
        case "2to1":
            assert_dialog = merge_dialog.merge_2to1()
            assert assert_dialog.text() == (
                "Should the competitor Olaf Scholz be removed, "
                "and every instance of that name (including sex and year of birth) "
                "in all events be replaced with competitor Robert Habeck?"
            )
            assert_dialog.ok()
        case _:
            raise RuntimeError("Unknown direction {direction}")

    rows = iter(RowIterator(table=competitor_page.table))
    assert next(rows) == [
        "Competitors  (5)",
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
    if direction != "1to2":
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
    if direction != "2to1":
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

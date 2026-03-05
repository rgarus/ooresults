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


from webtests.pageobjects.main_page import MainPage


def test_if_competitor_page_is_displayed_then_all_actions_are_displayed(
    main_page: MainPage,
):
    competitor_page = main_page.goto_competitors()
    assert competitor_page.actions.texts() == [
        "Reload",
        "Import ...",
        "Export ...",
        "Add competitor ...",
        "Edit competitor ...",
        "Delete competitor",
    ]


def test_if_no_row_is_selected_then_some_actions_are_disabled(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    assert competitor_page.actions.action("Reload").is_enabled()
    assert competitor_page.actions.action("Import ...").is_enabled()
    assert competitor_page.actions.action("Export ...").is_enabled()
    assert competitor_page.actions.action("Add competitor ...").is_enabled()
    assert competitor_page.actions.action("Edit competitor ...").is_disabled()
    assert competitor_page.actions.action("Delete competitor").is_disabled()


def test_if_a_row_is_selected_then_all_actions_are_enabled(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    competitor_page.table.select_row(i=2)

    assert competitor_page.actions.action("Reload").is_enabled()
    assert competitor_page.actions.action("Import ...").is_enabled()
    assert competitor_page.actions.action("Export ...").is_enabled()
    assert competitor_page.actions.action("Add competitor ...").is_enabled()
    assert competitor_page.actions.action("Edit competitor ...").is_enabled()
    assert competitor_page.actions.action("Delete competitor").is_enabled()


def test_if_competitor_page_is_selected_then_the_table_header_is_displayed(
    main_page: MainPage,
):
    competitor_page = main_page.goto_competitors()
    assert competitor_page.table.nr_of_columns() == 6
    assert competitor_page.table.headers() == [
        "First name",
        "Last name",
        "Gender",
        "Year",
        "Chip",
        "Club",
    ]


def test_if_filter_is_set_then_only_matching_rows_are_displayed(
    main_page: MainPage, competitor: None
):
    competitor_page = main_page.goto_competitors()
    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Christian",
        last_name="Lindner",
        gender="M",
        year="1979",
        chip="7754987",
        club="",
    )
    dialog.submit()

    dialog = competitor_page.actions.add()
    dialog.enter_values(
        first_name="Robert",
        last_name="Habeck",
        gender="M",
        year="1969",
        chip="7509749",
        club="",
    )
    dialog.submit()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 4
    assert competitor_page.table.nr_of_columns() == 6

    try:
        competitor_page.filter().set_text("hab")

        # check number of rows
        assert competitor_page.table.nr_of_rows() == 2
        assert competitor_page.table.nr_of_columns() == 6

        assert competitor_page.table.row(i=1) == [
            "Competitors  (3)",
        ]
        assert competitor_page.table.row(i=2) == [
            "Robert",
            "Habeck",
            "M",
            "1969",
            "7509749",
            "",
        ]
    finally:
        competitor_page.filter().set_text("")

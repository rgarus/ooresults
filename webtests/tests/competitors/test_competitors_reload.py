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
from webtests.tests.conftest import post


def test_if_a_competitor_is_added_by_another_user_then_it_is_displayed_after_reload(
    main_page: MainPage, competitor: None
):
    post(
        url="https://127.0.0.1:8080/competitor/add",
        data={
            "id": "",
            "first_name": "Robert",
            "last_name": "Habeck",
            "gender": "M",
            "year": "1969",
            "chip": "7509749",
            "club_id": "",
        },
    )
    competitor_page = main_page.goto_competitors()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 2
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (1)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
    ]

    competitor_page.actions.reload()

    # check number of rows
    assert competitor_page.table.nr_of_rows() == 3
    assert competitor_page.table.nr_of_columns() == 6

    assert competitor_page.table.row(i=1) == [
        "Competitors  (2)",
    ]
    assert competitor_page.table.row(i=2) == [
        "Annalena",
        "Baerbock",
        "F",
        "1980",
        "7379879",
        "",
    ]
    assert competitor_page.table.row(i=3) == [
        "Robert",
        "Habeck",
        "M",
        "1969",
        "7509749",
        "",
    ]

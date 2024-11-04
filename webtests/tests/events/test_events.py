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


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table
from webtests.pageobjects.tabs import Tabs


def test_all_actions_displayed(page):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    assert actions.texts() == [
        "Reload",
        "Add event ...",
        "Edit event ...",
        "Delete event",
    ]


def test_table_header(page):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_columns() == 7
    assert table.headers() == [
        "Name",
        "Date",
        "Key",
        "Publish",
        "Streaming",
        "Series",
        "Fields",
    ]


def test_events(page):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    elem = page.find_element(By.ID, "eve_name")
    elem.send_keys("Test-Lauf heute")

    page.execute_script("document.getElementById('eve_date').value = '2023-12-28'")

    elem = page.find_element(By.ID, "evnt.formAdd")
    elem = elem.find_element(By.XPATH, "button[@type='submit']")
    elem.click()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 1
    assert table.nr_of_columns() == 7

    assert table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "",
        "no",
        "",
        "",
        "",
    ]

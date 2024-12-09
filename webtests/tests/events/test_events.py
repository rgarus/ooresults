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


import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from webtests.pageobjects.actions import Actions
from webtests.pageobjects.events import AddEventDialog
from webtests.pageobjects.table import Table
from webtests.pageobjects.tabs import Tabs


def test_all_actions_displayed(page: webdriver.Firefox):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    assert actions.texts() == [
        "Reload",
        "Add event ...",
        "Edit event ...",
        "Delete event",
    ]


def test_table_header(page: webdriver.Firefox):
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


@pytest.fixture
def delete_events(page: webdriver.Firefox):
    Tabs(page=page).tab(text="Events").click()
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    for i in range(table.nr_of_rows()):
        table.select_row(1)

        actions = Actions(page=page, id="eve_actions")
        actions.action(text="Delete event").click()

        elem = page.find_element(By.ID, "evnt.formDelete")
        elem.find_element(By.XPATH, "button[@type='submit']").click()


def test_add_event_with_required_data(page, delete_events):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.check_values(
        name="",
        date="",
        key="",
        publish="no",
        series="",
        fields=[],
        streaming_address="",
        streaming_key="",
        streaming_enabled=False,
    )
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key=None,
        publish=None,
        series=None,
        fields=[],
        streaming_address=None,
        streaming_key=None,
        streaming_enabled=None,
    )
    dialog.submit()

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


def test_add_event_with_all_data(page, delete_events):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.check_values(
        name="",
        date="",
        key="",
        publish="no",
        series="",
        fields=[],
        streaming_address="",
        streaming_key="",
        streaming_enabled=False,
    )
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 1
    assert table.nr_of_columns() == 7

    assert table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]


def test_edit_event(page, delete_events):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 1
    assert table.nr_of_columns() == 7

    assert table.row(i=1) == [
        "Test-Lauf heute",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]

    table.select_row(1)

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Edit event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.check_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.enter_values(
        name="Test-Lauf morgen",
        date="2023-12-29",
        key="local",
        publish="no",
        series="Serie 2",
        fields=["field"],
        streaming_address="myhost:8081",
        streaming_key="",
        streaming_enabled=True,
    )
    dialog.submit()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 1
    assert table.nr_of_columns() == 7

    assert table.row(i=1) == [
        "Test-Lauf morgen",
        "2023-12-29",
        "***",
        "no",
        "",
        "Serie 2",
        "field",
    ]


def test_delete_event(page, delete_events):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.enter_values(
        name="Test-Lauf heute",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 1
    assert table.nr_of_columns() == 7

    table.select_row(1)

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Delete event").click()

    elem = page.find_element(By.ID, "evnt.formDelete")
    elem.find_element(By.XPATH, "button[@type='submit']").click()

    assert table.nr_of_rows() == 0
    assert table.nr_of_columns() == 7


def test_add_two_events(page, delete_events):
    tabs = Tabs(page=page)
    tabs.tab(text="Events").click()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.enter_values(
        name="Test-Lauf 1",
        date="2023-12-28",
        key="local-key",
        publish="yes",
        series="Serie",
        fields=["a", "b"],
        streaming_address="localhost:8081",
        streaming_key="abcde",
        streaming_enabled=True,
    )
    dialog.submit()

    actions = Actions(page=page, id="eve_actions")
    actions.action(text="Add event ...").click()

    dialog = AddEventDialog(page=page)
    dialog.enter_values(
        name="Test-Lauf 2",
        date="2023-12-29",
        key="local",
        publish="no",
        series="Serie",
        fields=["e", "f"],
        streaming_address="myhost:8081",
        streaming_key="secret-key",
        streaming_enabled=True,
    )
    dialog.submit()

    # number of rows
    table = Table(page=page, xpath="//table[@id='evnt.table']")
    assert table.nr_of_rows() == 2
    assert table.nr_of_columns() == 7

    assert table.row(i=1) == [
        "Test-Lauf 1",
        "2023-12-28",
        "***",
        "yes",
        "enabled",
        "Serie",
        "a, b",
    ]
    assert table.row(i=2) == [
        "Test-Lauf 2",
        "2023-12-29",
        "***",
        "no",
        "enabled",
        "Serie",
        "e, f",
    ]

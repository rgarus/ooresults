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


from typing import Optional
from typing import TypeVar

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import invisibility_of_element
from selenium.webdriver.support.wait import WebDriverWait

from webtests.controls.text_control import TextControl
from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table


T = TypeVar("T", bound="AddClubDialog")


class AddClubDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        self.page.find_element(By.ID, "clb.formAdd")
        return self

    def check_values(self, name: str) -> None:
        self.wait()

        assert name == TextControl(page=self.page, id="clb_name").get_text()

    def enter_values(self, name: Optional[str] = None) -> None:
        self.wait()

        if name is not None:
            TextControl(page=self.page, id="clb_name").set_text(text=name)

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "clb.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(invisibility_of_element(elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "clb.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(invisibility_of_element(elem))


class DeleteClubDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "clb.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(invisibility_of_element(elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "clb.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(invisibility_of_element(elem))


class ClubPage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = ClubActions(page=page)
        self.table = ClubTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="club.filter")

    def delete_clubs(self) -> None:
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class ClubActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="club.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def add(self) -> AddClubDialog:
        self.action(text="Add club ...").click()
        return AddClubDialog(page=self.page)

    def edit(self) -> AddClubDialog:
        self.action(text="Edit club ...").click()
        return AddClubDialog(page=self.page)

    def delete(self) -> DeleteClubDialog:
        self.action(text="Delete club").click()
        return DeleteClubDialog(page=self.page)


class ClubTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='clb.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddClubDialog:
        super().double_click_row(i=i)
        return AddClubDialog(page=self.page)

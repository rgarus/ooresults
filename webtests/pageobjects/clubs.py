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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webtests.controls.text_control import TextControl
from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table


T = TypeVar("T", bound="AddClubDialog")


class AddClubDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def wait(self: T) -> T:
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "clb.formAdd"))
        )
        return self

    def check_values(self, name: str) -> None:
        self.wait()

        assert name == TextControl(driver=self.driver, id="clb_name").get_text()

    def enter_values(self, name: Optional[str] = None) -> None:
        self.wait()

        if name is not None:
            TextControl(driver=self.driver, id="clb_name").set_text(text=name)

    def submit(self, wait_until_closed: bool = True) -> None:
        elem = self.driver.find_element(By.ID, "clb.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        if wait_until_closed:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element(element=elem)
            )

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "clb.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class DeleteClubDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def ok(self) -> None:
        elem = self.driver.find_element(By.ID, "clb.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "clb.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class ClubPage:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.actions = ClubActions(driver=driver)
        self.table = ClubTable(driver=driver)

    def filter(self) -> TextControl:
        return TextControl(driver=self.driver, id="club.filter")

    def select_club(self, name: str) -> None:
        for i in range(2, self.table.nr_of_rows() + 2):
            if self.table.row(i=i)[0] == name:
                self.table.select_row(i=i)
                break
        else:
            raise RuntimeError(f"Club {name} not found")

    def delete_club(self, name: str) -> None:
        self.select_club(name=name)
        self.actions.delete().ok()

    def delete_clubs(self) -> None:
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class ClubActions(Actions):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, id="club.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def add(self) -> AddClubDialog:
        self.action(text="Add club ...").click()
        return AddClubDialog(driver=self.driver)

    def edit(self) -> AddClubDialog:
        self.action(text="Edit club ...").click()
        return AddClubDialog(driver=self.driver)

    def delete(self) -> DeleteClubDialog:
        self.action(text="Delete club").click()
        return DeleteClubDialog(driver=self.driver)


class ClubTable(Table):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, xpath="//table[@id='clb.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddClubDialog:
        super().double_click_row(i=i)
        return AddClubDialog(driver=self.driver)

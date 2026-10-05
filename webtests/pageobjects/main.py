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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webtests.controls.text_control import TextControl
from webtests.pageobjects.table import Table


class SelectCompetitorDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.table = Table(driver=driver, xpath="//table[@id='main.comp.table']")

    def filter(self) -> TextControl:
        return TextControl(driver=self.driver, id="main.comp.filter")

    def select_competitor(self, first_name: str, last_name: str) -> None:
        for i in range(2, self.table.nr_of_rows() + 2):
            if self.table.row(i=i)[0:2] == [first_name, last_name]:
                self.table.select_row(i=i)
                break
        else:
            raise RuntimeError(f"Competitor {last_name}, {first_name} not found")

    def selected_row(self) -> Optional[int]:
        rows = self.table.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> None:
        elem = self.driver.find_element(By.ID, "main.competitorsDialog")
        self.table.double_click(i=i)
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def save(self) -> None:
        elem = self.driver.find_element(By.ID, "main.competitorsDialog")
        elem.find_element(By.XPATH, ".//button[text()='Save']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "main.competitorsDialog")
        elem.find_element(By.XPATH, ".//button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

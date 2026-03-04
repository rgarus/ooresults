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


from pathlib import Path
from typing import Optional
from typing import TypeVar

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webtests.controls.combobox_control import ComboboxControl
from webtests.controls.number_control import NumberControl
from webtests.controls.text_control import TextControl
from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table


T = TypeVar("T", bound="AddCompetitorDialog")


class AddCompetitorDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def wait(self: T) -> T:
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "comp.formAdd"))
        )
        return self

    def check_values(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        year: str,
        chip: str,
        club: str,
    ) -> None:
        self.wait()

        assert (
            first_name == TextControl(driver=self.driver, id="com_firstName").get_text()
        )
        assert (
            last_name == TextControl(driver=self.driver, id="com_lastName").get_text()
        )
        assert (
            gender
            == ComboboxControl(driver=self.driver, id="com_gender").selected_text()
        )
        assert year == NumberControl(driver=self.driver, id="com_year").get_text()
        assert chip == TextControl(driver=self.driver, id="com_chip").get_text()
        assert (
            club == ComboboxControl(driver=self.driver, id="com_clubId").selected_text()
        )

    def get_gender_list(self) -> list[str]:
        return ComboboxControl(driver=self.driver, id="com_gender").values()

    def get_club_list(self) -> list[str]:
        return ComboboxControl(driver=self.driver, id="com_clubId").values()

    def enter_values(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        gender: Optional[str] = None,
        year: Optional[str] = None,
        chip: Optional[str] = None,
        club: Optional[str] = None,
    ) -> None:
        self.wait()

        if first_name is not None:
            TextControl(driver=self.driver, id="com_firstName").set_text(
                text=first_name
            )
        if last_name is not None:
            TextControl(driver=self.driver, id="com_lastName").set_text(text=last_name)
        if gender is not None:
            ComboboxControl(driver=self.driver, id="com_gender").select_by_text(
                text=gender
            )
        if year is not None:
            NumberControl(driver=self.driver, id="com_year").set_text(text=year)
        if chip is not None:
            TextControl(driver=self.driver, id="com_chip").set_text(text=chip)
        if club is not None:
            ComboboxControl(driver=self.driver, id="com_clubId").select_by_text(
                text=club
            )

    def submit(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class ImportCompetitorDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.import.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def import_(self, path: Path) -> None:
        elem = self.driver.find_element(By.ID, "comp.import.form")
        elem.find_element(By.ID, "file1").send_keys(str(path))
        elem.find_element(By.XPATH, "button[text()='Import']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class ExportCompetitorDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.formExport")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class DeleteCompetitorDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def ok(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "comp.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class CompetitorPage:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.actions = CompetitorActions(driver=driver)
        self.table = CompetitorTable(driver=driver)

    def filter(self) -> TextControl:
        return TextControl(driver=self.driver, id="comp.filter")

    def select_competitor(self, first_name: str, last_name: str) -> None:
        for i in range(2, self.table.nr_of_rows() + 2):
            if self.table.row(i=i)[0:2] == (first_name, last_name):
                self.table.select_row(i=i)
                break
        else:
            raise RuntimeError(f"Competitor {last_name}, {first_name} not found")

    def delete_competitor(self, first_name: str, last_name: str) -> None:
        self.select_competitor(first_name=first_name, last_name=last_name)
        self.actions.delete().ok()

    def delete_competitors(self) -> None:
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class CompetitorActions(Actions):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, id="comp.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def import_(self) -> ImportCompetitorDialog:
        self.action(text="Import ...").click()
        return ImportCompetitorDialog(driver=self.driver)

    def export(self) -> ExportCompetitorDialog:
        self.action(text="Export ...").click()
        return ExportCompetitorDialog(driver=self.driver)

    def add(self) -> AddCompetitorDialog:
        self.action(text="Add competitor ...").click()
        return AddCompetitorDialog(driver=self.driver)

    def edit(self) -> AddCompetitorDialog:
        self.action(text="Edit competitor ...").click()
        return AddCompetitorDialog(driver=self.driver)

    def delete(self) -> DeleteCompetitorDialog:
        self.action(text="Delete competitor").click()
        return DeleteCompetitorDialog(driver=self.driver)


class CompetitorTable(Table):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, xpath="//table[@id='comp.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddCompetitorDialog:
        super().double_click_row(i=i)
        return AddCompetitorDialog(driver=self.driver)

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
from typing import List
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
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        WebDriverWait(self.page, 10).until(
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

        assert first_name == TextControl(page=self.page, id="com_firstName").get_text()
        assert last_name == TextControl(page=self.page, id="com_lastName").get_text()
        assert (
            gender == ComboboxControl(page=self.page, id="com_gender").selected_text()
        )
        assert year == NumberControl(page=self.page, id="com_year").get_text()
        assert chip == TextControl(page=self.page, id="com_chip").get_text()
        assert club == ComboboxControl(page=self.page, id="com_clubId").selected_text()

    def get_gender_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="com_gender").values()

    def get_club_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="com_clubId").values()

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
            TextControl(page=self.page, id="com_firstName").set_text(text=first_name)
        if last_name is not None:
            TextControl(page=self.page, id="com_lastName").set_text(text=last_name)
        if gender is not None:
            ComboboxControl(page=self.page, id="com_gender").select_by_text(text=gender)
        if year is not None:
            NumberControl(page=self.page, id="com_year").set_text(text=year)
        if chip is not None:
            TextControl(page=self.page, id="com_chip").set_text(text=chip)
        if club is not None:
            ComboboxControl(page=self.page, id="com_clubId").select_by_text(text=club)

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "comp.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "comp.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ImportCompetitorDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "comp.import.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def import_(self, path: Path) -> None:
        elem = self.page.find_element(By.ID, "comp.import.form")
        elem.find_element(By.ID, "file1").send_keys(str(path))
        elem.find_element(By.XPATH, "button[text()='Import']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ExportCompetitorDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "comp.formExport")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class DeleteCompetitorDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "comp.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "comp.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class CompetitorPage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = CompetitorActions(page=page)
        self.table = CompetitorTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="comp.filter")

    def delete_competitors(self) -> None:
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class CompetitorActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="comp.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def import_(self) -> ImportCompetitorDialog:
        self.action(text="Import ...").click()
        return ImportCompetitorDialog(page=self.page)

    def export(self) -> ExportCompetitorDialog:
        self.action(text="Export ...").click()
        return ExportCompetitorDialog(page=self.page)

    def add(self) -> AddCompetitorDialog:
        self.action(text="Add competitor ...").click()
        return AddCompetitorDialog(page=self.page)

    def edit(self) -> AddCompetitorDialog:
        self.action(text="Edit competitor ...").click()
        return AddCompetitorDialog(page=self.page)

    def delete(self) -> DeleteCompetitorDialog:
        self.action(text="Delete competitor").click()
        return DeleteCompetitorDialog(page=self.page)


class CompetitorTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='comp.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddCompetitorDialog:
        super().double_click_row(i=i)
        return AddCompetitorDialog(page=self.page)

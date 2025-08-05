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


T = TypeVar("T", bound="AddCourseDialog")


class AddCourseDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        WebDriverWait(self.page, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "cou.formAdd"))
        )
        return self

    def check_values(
        self,
        name: str,
        length: str,
        climb: str,
        controls: str,
    ):
        self.wait()

        assert name == TextControl(page=self.page, id="cou_name").get_text()
        assert length == TextControl(page=self.page, id="cou_length").get_text()
        assert climb == TextControl(page=self.page, id="cou_climb").get_text()
        assert controls == TextControl(page=self.page, id="cou_controls").get_text()

    def enter_values(
        self,
        name: Optional[str] = None,
        length: Optional[str] = None,
        climb: Optional[str] = None,
        controls: Optional[str] = None,
    ):
        self.wait()

        if name is not None:
            TextControl(page=self.page, id="cou_name").set_text(text=name)
        if length is not None:
            TextControl(page=self.page, id="cou_length").set_text(text=length)
        if climb is not None:
            TextControl(page=self.page, id="cou_climb").set_text(text=climb)
        if controls is not None:
            TextControl(page=self.page, id="cou_controls").set_text(text=controls)

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ImportCourseDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formImport")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ExportCourseDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formExport")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(elem))


class DeleteCourseDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cou.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(elem))


class CoursePage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = CourseActions(page=page)
        self.table = CourseTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="cour.filter")

    def get_event_name(self) -> str:
        return self.page.find_element(By.ID, "cou.event_name").text

    def get_event_date(self) -> str:
        return self.page.find_element(By.ID, "cou.event_date").text

    def delete_courses(self):
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class CourseActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="cour.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def import_(self) -> ImportCourseDialog:
        self.action(text="Import ...").click()
        return ImportCourseDialog(page=self.page)

    def export(self) -> ExportCourseDialog:
        self.action(text="Export ...").click()
        return ExportCourseDialog(page=self.page)

    def add(self) -> AddCourseDialog:
        self.action(text="Add course ...").click()
        return AddCourseDialog(page=self.page)

    def edit(self) -> AddCourseDialog:
        self.action(text="Edit course ...").click()
        return AddCourseDialog(page=self.page)

    def delete(self) -> DeleteCourseDialog:
        self.action(text="Delete course").click()
        return DeleteCourseDialog(page=self.page)


class CourseTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='cou.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddCourseDialog:
        super().double_click_row(i=i)
        return AddCourseDialog(page=self.page)

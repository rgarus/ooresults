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

from webtests.controls.checkbox_control import CheckboxControl
from webtests.controls.combobox_control import ComboboxControl
from webtests.controls.number_control import NumberControl
from webtests.controls.text_control import TextControl
from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table


T = TypeVar("T", bound="AddClassDialog")


class AddClassDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        WebDriverWait(self.page, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "cls.formAdd"))
        )
        return self

    def check_values(
        self,
        name: str,
        short_name: str,
        course: str,
        voided_legs: str,
        type: str,
        use_start_control: str,
        apply_handicap: bool,
        mass_start: str,
        time_limit: str,
        penalty_controls: str,
        penalty_time_limit: str,
    ):
        self.wait()

        assert name == TextControl(page=self.page, id="cla_name").get_text()
        assert short_name == TextControl(page=self.page, id="cla_shortName").get_text()
        assert (
            course == ComboboxControl(page=self.page, id="cla_courseId").selected_text()
        )
        assert (
            voided_legs == TextControl(page=self.page, id="cla_voidedLegs").get_text()
        )
        assert type == ComboboxControl(page=self.page, id="cla_type").selected_text()
        assert (
            use_start_control
            == ComboboxControl(page=self.page, id="cla_startControl").selected_text()
        )
        assert (
            apply_handicap
            == CheckboxControl(page=self.page, id="cla_handicap").is_checked()
        )
        assert mass_start == TextControl(page=self.page, id="cla_massStart").get_text()
        assert time_limit == TextControl(page=self.page, id="cla_timeLimit").get_text()
        assert (
            penalty_controls
            == NumberControl(page=self.page, id="cla_penaltyControls").get_text()
        )
        assert (
            penalty_time_limit
            == NumberControl(page=self.page, id="cla_penaltyOvertime").get_text()
        )

    def get_course_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="cla_courseId").values()

    def get_type_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="cla_type").values()

    def get_use_start_control_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="cla_startControl").values()

    def enter_values(
        self,
        name: Optional[str] = None,
        short_name: Optional[str] = None,
        course: Optional[str] = None,
        voided_legs: Optional[str] = None,
        type: Optional[str] = None,
        use_start_control: Optional[str] = None,
        apply_handicap: Optional[bool] = None,
        mass_start: Optional[str] = None,
        time_limit: Optional[str] = None,
        penalty_controls: Optional[str] = None,
        penalty_time_limit: Optional[str] = None,
    ):
        self.wait()

        if name is not None:
            TextControl(page=self.page, id="cla_name").set_text(text=name)
        if short_name is not None:
            TextControl(page=self.page, id="cla_shortName").set_text(text=short_name)
        if course is not None:
            ComboboxControl(page=self.page, id="cla_courseId").select_by_text(
                text=course
            )
        if voided_legs is not None:
            TextControl(page=self.page, id="cla_voidedLegs").set_text(text=voided_legs)
        if type is not None:
            ComboboxControl(page=self.page, id="cla_type").select_by_text(text=type)
        if use_start_control is not None:
            ComboboxControl(page=self.page, id="cla_startControl").select_by_text(
                text=use_start_control
            )
        if apply_handicap is not None:
            CheckboxControl(page=self.page, id="cla_handicap").set_state(
                checked=apply_handicap
            )
        if mass_start is not None:
            TextControl(page=self.page, id="cla_massStart").set_text(text=mass_start)
        if time_limit is not None:
            TextControl(page=self.page, id="cla_timeLimit").set_text(text=time_limit)
        if penalty_controls is not None:
            NumberControl(page=self.page, id="cla_penaltyControls").set_text(
                text=penalty_controls
            )
        if penalty_time_limit is not None:
            NumberControl(page=self.page, id="cla_penaltyOvertime").set_text(
                text=penalty_time_limit
            )

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "cls.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cls.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ImportClassDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cls.import.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def import_(self, path: Path) -> None:
        elem = self.page.find_element(By.ID, "cls.import.form")
        elem.find_element(By.ID, "file1").send_keys(str(path))
        elem.find_element(By.XPATH, "button[text()='Import']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ExportClassDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cls.export.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class DeleteClassDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "cls.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "cls.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ClassPage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = ClassActions(page=page)
        self.table = ClassTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="clas.filter")

    def get_event_name(self) -> str:
        return self.page.find_element(By.ID, "clas.event_name").text

    def get_event_date(self) -> str:
        return self.page.find_element(By.ID, "clas.event_date").text

    def delete_classes(self):
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class ClassActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="clas.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def import_(self) -> ImportClassDialog:
        self.action(text="Import ...").click()
        return ImportClassDialog(page=self.page)

    def export(self) -> ExportClassDialog:
        self.action(text="Export ...").click()
        return ExportClassDialog(page=self.page)

    def add(self) -> AddClassDialog:
        self.action(text="Add class ...").click()
        return AddClassDialog(page=self.page)

    def edit(self) -> AddClassDialog:
        self.action(text="Edit class ...").click()
        return AddClassDialog(page=self.page)

    def delete(self) -> DeleteClassDialog:
        self.action(text="Delete class").click()
        return DeleteClassDialog(page=self.page)


class ClassTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='cls.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddClassDialog:
        super().double_click_row(i=i)
        return AddClassDialog(page=self.page)

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


T = TypeVar("T", bound="AddEntryDialog")


class AddEntryDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        WebDriverWait(self.page, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "entr.formAdd"))
        )
        return self

    def check_values(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        year: str,
        chip: str,
        club_name: str,
        class_name: str,
        not_competing: bool,
        start_time: str,
        status: str,
        result: Optional[str] = None,
    ):
        self.wait()
        p = self.page
        assert first_name == TextControl(page=p, id="ent_firstName").get_text()
        assert last_name == TextControl(page=p, id="ent_lastName").get_text()
        assert gender == ComboboxControl(page=p, id="ent_gender").selected_text()
        assert year == NumberControl(page=p, id="ent_year").get_text()
        assert chip == TextControl(page=p, id="ent_chip").get_text()
        assert club_name == ComboboxControl(page=p, id="ent_clubId").selected_text()
        assert class_name == ComboboxControl(page=p, id="ent_classId").selected_text()
        assert (
            not_competing == CheckboxControl(page=p, id="ent_notCompeting").is_checked()
        )
        assert start_time == TextControl(page=p, id="ent_startTime").get_text()
        assert status == ComboboxControl(page=p, id="ent_status").selected_text()
        if result is not None:
            assert result == ComboboxControl(page=p, id="ent_result").selected_text()

    def get_gender_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="ent_gender").values()

    def get_club_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="ent_clubId").values()

    def get_class_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="ent_classId").values()

    def get_status_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="ent_status").values()

    def get_result_list(self) -> List[str]:
        return ComboboxControl(page=self.page, id="ent_result").values()

    def enter_values(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        gender: Optional[str] = None,
        year: Optional[str] = None,
        chip: Optional[str] = None,
        club_name: Optional[str] = None,
        class_name: Optional[str] = None,
        not_competing: Optional[bool] = None,
        start_time: Optional[str] = None,
        status: Optional[str] = None,
        result: Optional[str] = None,
    ):
        self.wait()
        p = self.page
        if first_name is not None:
            TextControl(page=p, id="ent_firstName").set_text(text=first_name)
        if last_name is not None:
            TextControl(page=p, id="ent_lastName").set_text(text=last_name)
        if gender is not None:
            ComboboxControl(page=p, id="ent_gender").select_by_text(text=gender)
        if year is not None:
            NumberControl(page=p, id="ent_year").set_text(text=year)
        if chip is not None:
            TextControl(page=p, id="ent_chip").set_text(text=chip)
        if club_name is not None:
            ComboboxControl(page=p, id="ent_clubId").select_by_text(text=club_name)
        if class_name is not None:
            ComboboxControl(page=p, id="ent_classId").select_by_text(text=class_name)
        if not_competing is not None:
            CheckboxControl(page=p, id="ent_notCompeting").set_state(
                checked=not_competing
            )
        if start_time is not None:
            TextControl(page=p, id="ent_startTime").set_text(text=start_time)
        if status is not None:
            ComboboxControl(page=p, id="ent_status").select_by_text(text=status)
        if result is not None:
            ComboboxControl(page=p, id="ent_result").select_by_text(text=result)

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "entr.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "entr.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ImportEntryDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "entr.import.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def import_(self, path: Path) -> None:
        elem = self.page.find_element(By.ID, "entr.import.form")
        elem.find_element(By.ID, "file1").send_keys(str(path))
        elem.find_element(By.XPATH, "button[text()='Import']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class ExportEntryDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "entr.export.form")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class DeleteEntryDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "entr.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "entr.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class EditSplitTimesDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def close(self) -> None:
        elem = self.page.find_element(By.ID, "entr.formSplitTimes")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class EntryPage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = EntryActions(page=page)
        self.table = EntryTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="entr.filter")

    def get_event_name(self) -> str:
        return self.page.find_element(By.ID, "entr.event_name").text

    def get_event_date(self) -> str:
        return self.page.find_element(By.ID, "entr.event_date").text

    def delete_entries(self):
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class EntryActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="entr.actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def import_(self) -> ImportEntryDialog:
        self.action(text="Import ...").click()
        return ImportEntryDialog(page=self.page)

    def export(self) -> ExportEntryDialog:
        self.action(text="Export ...").click()
        return ExportEntryDialog(page=self.page)

    def add(self) -> AddEntryDialog:
        self.action(text="Add entry ...").click()
        return AddEntryDialog(page=self.page)

    def edit(self) -> AddEntryDialog:
        self.action(text="Edit entry ...").click()
        return AddEntryDialog(page=self.page)

    def delete(self) -> DeleteEntryDialog:
        self.action(text="Delete entry").click()
        return DeleteEntryDialog(page=self.page)

    def edit_split_times(self) -> EditSplitTimesDialog:
        self.action(text="Edit split times ...").click()
        return EditSplitTimesDialog(page=self.page)


class EntryTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='entr.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddEntryDialog:
        super().double_click_row(i=i)
        return AddEntryDialog(page=self.page)

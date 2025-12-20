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

from webtests.controls.checkbox_control import CheckboxControl
from webtests.controls.date_control import DateControl
from webtests.controls.text_control import TextControl
from webtests.pageobjects.actions import Actions
from webtests.pageobjects.table import Table


T = TypeVar("T", bound="AddEventDialog")


class AddEventDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def wait(self: T) -> T:
        WebDriverWait(self.page, 10).until(
            EC.visibility_of_element_located(locator=(By.ID, "evnt.formAdd"))
        )
        return self

    def check_values(
        self,
        name: str,
        date: str,
        key: str,
        publish: bool,
        series: str,
        fields: list[str],
        streaming_address: str,
        streaming_key: str,
        streaming_enabled: bool,
    ) -> None:
        self.wait()

        assert name == TextControl(page=self.page, id="eve_name").get_text()
        assert date == DateControl(page=self.page, id="eve_date").get_date()
        assert key == TextControl(page=self.page, id="eve_key").get_text()
        assert publish == CheckboxControl(page=self.page, id="eve_publish").is_checked()
        assert series == TextControl(page=self.page, id="eve_series").get_text()
        assert (
            ", ".join(fields) == TextControl(page=self.page, id="eve_fields").get_text()
        )
        assert (
            streaming_address
            == TextControl(page=self.page, id="eve_streamingAddress").get_text()
        )
        assert (
            streaming_key
            == TextControl(page=self.page, id="eve_streamingKey").get_text()
        )
        assert (
            streaming_enabled
            == CheckboxControl(page=self.page, id="eve_streamingEnabled").is_checked()
        )

    def enter_values(
        self,
        name: Optional[str] = None,
        date: Optional[str] = None,
        key: Optional[str] = None,
        publish: Optional[bool] = None,
        series: Optional[str] = None,
        fields: Optional[list[str]] = None,
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ) -> None:
        self.wait()

        if name is not None:
            TextControl(page=self.page, id="eve_name").set_text(text=name)
        if date is not None:
            DateControl(page=self.page, id="eve_date").set_date(date=date)
        if key is not None:
            TextControl(page=self.page, id="eve_key").set_text(text=key)
        if publish is not None:
            CheckboxControl(page=self.page, id="eve_publish").set_state(checked=publish)
        if series is not None:
            TextControl(page=self.page, id="eve_series").set_text(text=series)
        if fields is not None:
            TextControl(page=self.page, id="eve_fields").set_text(
                text=", ".join(fields)
            )
        if streaming_address is not None:
            TextControl(page=self.page, id="eve_streamingAddress").set_text(
                text=streaming_address
            )
        if streaming_key is not None:
            TextControl(page=self.page, id="eve_streamingKey").set_text(
                text=streaming_key
            )
        if streaming_enabled is not None:
            CheckboxControl(page=self.page, id="eve_streamingEnabled").set_state(
                checked=streaming_enabled
            )

    def submit(self) -> None:
        elem = self.page.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class DeleteEventDialog:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page

    def ok(self) -> None:
        elem = self.page.find_element(By.ID, "evnt.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.page.find_element(By.ID, "evnt.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.page, 10).until(EC.invisibility_of_element(element=elem))


class EventPage:
    def __init__(self, page: webdriver.Remote) -> None:
        self.page = page
        self.actions = EventActions(page=page)
        self.table = EventTable(page=page)

    def filter(self) -> TextControl:
        return TextControl(page=self.page, id="eve_filter")

    def get_event_name(self) -> str:
        return self.page.find_element(By.ID, "evnt.event_name").text

    def get_event_date(self) -> str:
        return self.page.find_element(By.ID, "evnt.event_date").text

    def delete_events(self):
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class EventActions(Actions):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, id="eve_actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def add(self) -> AddEventDialog:
        self.action(text="Add event ...").click()
        return AddEventDialog(page=self.page)

    def edit(self) -> AddEventDialog:
        self.action(text="Edit event ...").click()
        return AddEventDialog(page=self.page)

    def delete(self) -> DeleteEventDialog:
        self.action(text="Delete event").click()
        return DeleteEventDialog(page=self.page)


class EventTable(Table):
    def __init__(self, page: webdriver.Remote) -> None:
        super().__init__(page=page, xpath="//table[@id='evnt.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddEventDialog:
        super().double_click_row(i=i)
        return AddEventDialog(page=self.page)

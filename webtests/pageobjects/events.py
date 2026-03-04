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
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def wait(self: T) -> T:
        WebDriverWait(self.driver, 10).until(
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

        assert name == TextControl(driver=self.driver, id="eve_name").get_text()
        assert date == DateControl(driver=self.driver, id="eve_date").get_date()
        assert key == TextControl(driver=self.driver, id="eve_key").get_text()
        assert (
            publish
            == CheckboxControl(driver=self.driver, id="eve_publish").is_checked()
        )
        assert series == TextControl(driver=self.driver, id="eve_series").get_text()
        assert (
            ", ".join(fields)
            == TextControl(driver=self.driver, id="eve_fields").get_text()
        )
        assert (
            streaming_address
            == TextControl(driver=self.driver, id="eve_streamingAddress").get_text()
        )
        assert (
            streaming_key
            == TextControl(driver=self.driver, id="eve_streamingKey").get_text()
        )
        assert (
            streaming_enabled
            == CheckboxControl(
                driver=self.driver, id="eve_streamingEnabled"
            ).is_checked()
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
            TextControl(driver=self.driver, id="eve_name").set_text(text=name)
        if date is not None:
            DateControl(driver=self.driver, id="eve_date").set_date(date=date)
        if key is not None:
            TextControl(driver=self.driver, id="eve_key").set_text(text=key)
        if publish is not None:
            CheckboxControl(driver=self.driver, id="eve_publish").set_state(
                checked=publish
            )
        if series is not None:
            TextControl(driver=self.driver, id="eve_series").set_text(text=series)
        if fields is not None:
            TextControl(driver=self.driver, id="eve_fields").set_text(
                text=", ".join(fields)
            )
        if streaming_address is not None:
            TextControl(driver=self.driver, id="eve_streamingAddress").set_text(
                text=streaming_address
            )
        if streaming_key is not None:
            TextControl(driver=self.driver, id="eve_streamingKey").set_text(
                text=streaming_key
            )
        if streaming_enabled is not None:
            CheckboxControl(driver=self.driver, id="eve_streamingEnabled").set_state(
                checked=streaming_enabled
            )

    def submit(self) -> None:
        elem = self.driver.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Save']")
        elem.click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[text()='Cancel']")
        elem.click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class DeleteEventDialog:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def ok(self) -> None:
        elem = self.driver.find_element(By.ID, "evnt.formDelete")
        elem.find_element(By.XPATH, "button[text()='Delete']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))

    def cancel(self) -> None:
        elem = self.driver.find_element(By.ID, "evnt.formDelete")
        elem.find_element(By.XPATH, "button[text()='Cancel']").click()
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(element=elem))


class EventPage:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.actions = EventActions(driver=driver)
        self.table = EventTable(driver=driver)

    def filter(self) -> TextControl:
        return TextControl(driver=self.driver, id="eve_filter")

    def get_event_name(self) -> str:
        return self.driver.find_element(By.ID, "evnt.event_name").text

    def get_event_date(self) -> str:
        return self.driver.find_element(By.ID, "evnt.event_date").text

    def select_event(self, name: str) -> None:
        for i in range(2, self.table.nr_of_rows() + 2):
            if self.table.row(i=i)[0] == name:
                self.table.select_row(i=i)
                break
        else:
            raise RuntimeError(f"Event {name} not found")

    def delete_event(self, name: str) -> None:
        self.select_event(name=name)
        self.actions.delete().ok()

    def delete_events(self) -> None:
        for i in range(self.table.nr_of_rows() - 1):
            self.table.select_row(2)
            self.actions.delete().ok()


class EventActions(Actions):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, id="eve_actions")

    def reload(self) -> None:
        self.action(text="Reload").click()

    def add(self) -> AddEventDialog:
        self.action(text="Add event ...").click()
        return AddEventDialog(driver=self.driver)

    def edit(self) -> AddEventDialog:
        self.action(text="Edit event ...").click()
        return AddEventDialog(driver=self.driver)

    def delete(self) -> DeleteEventDialog:
        self.action(text="Delete event").click()
        return DeleteEventDialog(driver=self.driver)


class EventTable(Table):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, xpath="//table[@id='evnt.table']")

    def selected_row(self) -> Optional[int]:
        rows = self.selected_rows()

        if len(rows) >= 2:
            raise RuntimeError(f"Multiple rows selected: {rows}")
        else:
            return rows[0] if rows else None

    def double_click_row(self, i: int) -> AddEventDialog:
        super().double_click_row(i=i)
        return AddEventDialog(driver=self.driver)

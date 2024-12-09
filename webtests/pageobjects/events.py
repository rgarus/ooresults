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


from typing import List
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class AddEventDialog:
    def __init__(self, page: webdriver.Firefox):
        self.page = page

    def check_values(
        self,
        name: str,
        date: str,
        key: str,
        publish: str,
        series: str,
        fields: List[str],
        streaming_address: str,
        streaming_key: str,
        streaming_enabled: bool,
    ):
        assert name == self.page.find_element(By.ID, "eve_name").get_attribute("value")
        assert date == self.page.find_element(By.ID, "eve_date").get_attribute("value")
        assert key == self.page.find_element(By.ID, "eve_key").get_attribute("value")
        select = Select(self.page.find_element(By.ID, "eve_publish"))
        assert publish == select.first_selected_option.text
        assert series == self.page.find_element(By.ID, "eve_series").get_attribute(
            "value"
        )
        assert ", ".join(fields) == self.page.find_element(
            By.ID, "eve_fields"
        ).get_attribute("value")
        assert streaming_address == self.page.find_element(
            By.ID, "eve_streamingAddress"
        ).get_attribute("value")
        assert streaming_key == self.page.find_element(
            By.ID, "eve_streamingKey"
        ).get_attribute("value")
        checked = (
            self.page.find_element(By.ID, "eve_streamingEnabled").get_attribute(
                "checked"
            )
            == "true"
        )
        print("####", streaming_enabled, checked)
        assert streaming_enabled == checked

    def enter_values(
        self,
        name: Optional[str] = None,
        date: Optional[str] = None,
        key: Optional[str] = None,
        publish: Optional[str] = None,
        series: Optional[str] = None,
        fields: Optional[List[str]] = None,
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ):
        if name is not None:
            elem = self.page.find_element(By.ID, "eve_name")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(name)
        if date is not None:
            self.page.execute_script(
                f"document.getElementById('eve_date').value = '{date}'"
            )
        if key is not None:
            elem = self.page.find_element(By.ID, "eve_key")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(key)
        if publish is not None:
            select = Select(self.page.find_element(By.ID, "eve_publish"))
            select.select_by_visible_text(publish)
        if series is not None:
            elem = self.page.find_element(By.ID, "eve_series")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(series)
        if fields is not None:
            elem = self.page.find_element(By.ID, "eve_fields")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(", ".join(fields))
        if streaming_address is not None:
            elem = self.page.find_element(By.ID, "eve_streamingAddress")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(streaming_address)
        if streaming_key is not None:
            elem = self.page.find_element(By.ID, "eve_streamingKey")
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(streaming_key)
        if streaming_enabled is not None:
            checked = (
                self.page.find_element(By.ID, "eve_streamingEnabled").get_attribute(
                    "checked"
                )
                == "true"
            )
            if streaming_enabled != checked:
                self.page.find_element(By.ID, "eve_streamingEnabled").click()

    def submit(self):
        elem = self.page.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[@type='submit']")
        elem.click()

    def cancel(self):
        elem = self.page.find_element(By.ID, "evnt.formAdd")
        elem = elem.find_element(By.XPATH, "button[@type='cancel']")
        elem.click()

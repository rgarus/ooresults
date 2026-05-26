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


from selenium import webdriver
from selenium.webdriver.common.by import By


class RadioGroupControl:
    def __init__(self, driver: webdriver.Remote, name: str):
        self.driver = driver
        self.name = name

    def select(self, text: str) -> None:
        radiobuttons = self.driver.find_elements(By.NAME, self.name)
        for button in radiobuttons:
            label = button.find_element(By.XPATH, "../label")
            if label and label.text == text:
                if not button.get_attribute("disabled") == "true":
                    if not button.get_attribute("checked") == "true":
                        button.click()
                        break
                else:
                    raise RuntimeError("RadioButton is disabled")
        else:
            raise RuntimeError("RadioButton not found")

    def selected(self) -> str:
        radiobuttons = self.driver.find_elements(By.NAME, self.name)
        for button in radiobuttons:
            if button.is_displayed() and button.get_attribute("checked") == "true":
                label = button.find_element(By.XPATH, "../label")
                return label.text
        raise RuntimeError("RadioButton not found")

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


class Si1Page:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.handle = ""

    def open(self) -> None:
        # Opens a new tab and switches to new tab
        self.driver.switch_to.new_window("tab")
        assert self.driver.title == ""
        self.handle = self.driver.current_window_handle
        self.driver.get("https://admin:admin@localhost:8080/si1?view=1")
        assert self.driver.title == "SI reader"

    def close(self) -> None:
        self.driver.switch_to.window(self.handle)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_message(self) -> str:
        return self.driver.find_element(By.ID, "si1.message").text

    def get_line_1(self) -> str:
        return self.driver.find_element(By.ID, "si1.line_1").text

    def get_line_2(self) -> str:
        return self.driver.find_element(By.ID, "si1.line_2").text

    def get_line_3(self) -> str:
        return self.driver.find_element(By.ID, "si1.line_3").text

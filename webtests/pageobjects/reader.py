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
from selenium.webdriver.support.color import Color

from webtests.pageobjects.table import Table


class ReaderPage:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver
        self.table = ReaderTable(driver=driver)

    def get_event_name(self) -> str:
        return self.driver.find_element(By.ID, "read.event_name").text

    def get_event_date(self) -> str:
        return self.driver.find_element(By.ID, "read.event_date").text

    def get_reader_status(self) -> str:
        return self.driver.find_element(By.ID, "read.reader_status").text


class ReaderTable(Table):
    GREEN = Color.from_string("#70ff70")
    YELLOW = Color.from_string("#ffff00")
    RED = Color.from_string("#ff7070")

    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, xpath="//table[@id='read.messages']")

    def background_color_of_row(self, i: int) -> Color:
        rows = self._table().find_elements(By.XPATH, ".//tbody//tr")
        rows = [row for row in rows if row.is_displayed()]
        return Color.from_string(rows[i - 1].value_of_css_property("background-color"))

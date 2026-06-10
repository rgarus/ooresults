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

from webtests.pageobjects.table import Table


class SiReaderPage:
    def __init__(self, driver: webdriver.Remote, handle: str) -> None:
        self.driver = driver
        self.handle = handle
        self.table = SiReaderTable(driver=driver)

    def close(self) -> None:
        self.driver.switch_to.window(self.handle)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_event_name(self) -> str:
        return self.driver.find_element(By.ID, "si2.event_name").text

    def get_event_date(self) -> str:
        return self.driver.find_element(By.ID, "si2.event_date").text

    def get_reader_status(self) -> str:
        return self.driver.find_element(By.ID, "si2.reader_status").text


class SiReaderTable(Table):
    def __init__(self, driver: webdriver.Remote) -> None:
        super().__init__(driver=driver, xpath="//table[@id='si2.messages']")

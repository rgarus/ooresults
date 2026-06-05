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


from typing import TypeVar

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


T = TypeVar("T", bound="AlertWindow")


class AlertWindow:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def wait(self: T, timeout: int = 5) -> T:
        WebDriverWait(driver=self.driver, timeout=timeout).until(EC.alert_is_present())
        return self

    def accept(self) -> None:
        self.wait()
        Alert(self.driver).accept()

    def dismiss(self) -> None:
        self.wait()
        Alert(self.driver).dismiss()

    def get_text(self) -> str:
        self.wait()
        return Alert(self.driver).text

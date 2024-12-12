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


class DateControl:
    def __init__(self, page: webdriver.Remote, id: str):
        self.page = page
        self.elem = page.find_element(By.ID, id)

    def is_disabled(self) -> bool:
        return self.elem.get_attribute("disabled") == "true"

    def is_enabled(self) -> bool:
        return not self.is_disabled()

    def set_date(self, date: str) -> None:
        if self.is_enabled():
            self.elem.send_keys(date)
        else:
            raise RuntimeError("Date control is disabled")

    def get_date(self) -> str:
        if self.is_enabled():
            return self.elem.get_attribute("value")

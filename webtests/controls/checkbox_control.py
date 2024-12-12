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


class CheckboxControl:
    def __init__(self, page: webdriver.Remote, id: str):
        self.page = page
        self.elem = page.find_element(By.ID, id)

    def is_disabled(self) -> bool:
        return self.elem.get_attribute("disabled") == "true"

    def is_enabled(self) -> bool:
        return not self.is_disabled()

    def is_checked(self) -> bool:
        return self.elem.get_attribute("checked") == "true"

    def click(self) -> None:
        if self.is_enabled():
            self.elem.click()
        else:
            raise RuntimeError("Checkbox control is disabled")

    def set_state(self, checked: bool) -> None:
        if self.is_enabled():
            if self.is_checked() != checked:
                self.elem.click()
        else:
            raise RuntimeError("Checkbox control is disabled")

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


from selenium.webdriver.remote.webelement import WebElement


class ButtonControl:
    def __init__(self, elem: WebElement):
        self.elem = elem

    def is_disabled(self) -> bool:
        return self.elem.get_attribute("disabled") == "true"

    def is_enabled(self) -> bool:
        return not self.is_disabled()

    def click(self) -> None:
        if self.is_enabled():
            self.elem.click()
        else:
            raise RuntimeError("Button control is disabled")

    def text(self) -> str:
        return self.elem.text
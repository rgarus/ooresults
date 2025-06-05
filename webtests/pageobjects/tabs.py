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

from selenium import webdriver
from selenium.webdriver.common.by import By

from webtests.controls.button_control import ButtonControl


class Tab(ButtonControl):
    def is_selected(self) -> bool:
        return int(self.elem.value_of_css_property("font-weight")) >= 700


class Tabs:
    def __init__(self, page: webdriver.Remote):
        self.page = page

    def tabs(self) -> List[Tab]:
        elem = self.page.find_element(By.ID, "tabs")
        return [Tab(b) for b in elem.find_elements(By.XPATH, "button")]

    def texts(self) -> List[str]:
        texts = []
        for tab in self.tabs():
            texts.append(tab.text())
        return texts

    def tab(self, text: str) -> Tab:
        for tab in self.tabs():
            if tab.text() == text:
                return tab
        raise RuntimeError("Tab not found")

    def selected_tab(self) -> Tab:
        selected_tabs = []
        for tab in self.tabs():
            if tab.is_selected():
                selected_tabs.append(tab)

        if len(selected_tabs) == 1:
            return selected_tabs[0]
        else:
            raise RuntimeError(f"Selected tabs: {[t.text() for t in selected_tabs]}")

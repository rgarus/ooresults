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


class Action(ButtonControl):
    pass


class Actions:
    def __init__(self, page: webdriver.Remote, id: str):
        self.page = page
        self.id = id

    def actions(self) -> List[Action]:
        elem = self.page.find_element(By.ID, self.id)
        return [Action(b) for b in elem.find_elements(By.XPATH, "button")]

    def texts(self) -> List[str]:
        texts = []
        for action in self.actions():
            texts.append(action.text())
        return texts

    def action(self, text: str) -> Action:
        for action in self.actions():
            if action.text() == text:
                return action
        raise RuntimeError("Action not found")

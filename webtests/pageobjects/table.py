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
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By


class Table:
    def __init__(self, page: webdriver.Remote, xpath: str):
        self.page = page
        self.xpath = xpath

    def _table(self):
        return self.page.find_element(By.XPATH, self.xpath)

    def nr_of_rows(self) -> int:
        return len(self._table().find_elements(By.XPATH, ".//tbody//tr"))

    def nr_of_columns(self) -> int:
        return len(self._table().find_elements(By.XPATH, ".//thead//tr//th"))

    def headers(self) -> List[str]:
        headers = []
        for h in self._table().find_elements(By.XPATH, ".//thead//tr//th"):
            headers.append(h.text)
        return headers

    def row(self, i: int) -> List[str]:
        content = []
        for cell in self._table().find_elements(By.XPATH, f".//tbody//tr[{i}]//td"):
            content.append(cell.text)
        if content:
            return content
        else:
            raise RuntimeError("Row not found")

    def select_row(self, i: int) -> None:
        self._table().find_elements(By.XPATH, f".//tbody//tr[{i}]//td")[0].click()

    def selected_row(self) -> Optional[int]:
        for i, row in enumerate(self._table().find_elements(By.XPATH, ".//tbody//tr")):
            if row.value_of_css_property("background-color") == "rgb(165, 42, 42)":
                return i + 1
        else:
            return None

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


from lxml import etree
from lxml.etree import Element


class Html:
    def __init__(self, text: str) -> None:
        self.html: Element = etree.HTML(text=text)
        assert self.html is not None

    def findall(self, path: str) -> list[Element]:
        return self.html.findall(path=path)

    def find(self, path: str) -> Element:
        elem = self.html.find(path=path)

        assert elem is not None, f"Path not found: {path}"
        return elem

    def find_not(self, path: str) -> None:
        assert self.html.find(path=path) is None, f"Path found: {path}"

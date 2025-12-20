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


import subprocess
import sys
import tempfile

import pytest
import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture(scope="session")
def ooresults_server() -> None:
    with tempfile.TemporaryDirectory() as d_name:
        p = subprocess.Popen([sys.executable, "-m", "ooresults.server", "-p", d_name])
        yield
        p.kill()
        p.wait(timeout=10)


@pytest.fixture(scope="module")
def page(ooresults_server) -> webdriver.Firefox:
    driver = webdriver.Firefox()
    driver.get("https://admin:admin@localhost:8080")
    assert "ooresults" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "Administration")
    elem.click()
    yield driver
    driver.quit()


def post(url: str, data: dict[str, str]):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    r = requests.post(
        url=url,
        auth=("admin", "admin"),
        verify=False,
        data=data,
    )
    assert r.status_code == 200

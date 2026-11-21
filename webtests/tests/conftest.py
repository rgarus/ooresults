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


import pathlib
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator

import pytest
import requests
import urllib3
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from webtests.pageobjects.main_page import MainPage


pytest_plugins = [
    "webtests.pytest_plugins.close_popups",
]


@pytest.fixture(scope="session")
def ooresults_server() -> Iterator[subprocess.Popen]:
    with tempfile.TemporaryDirectory() as d_name:
        p = subprocess.Popen([sys.executable, "-m", "ooresults.server", "-p", d_name])
        yield p
        p.kill()
        p.wait(timeout=10)

        # In Windows, the database file continues to be accessed for a short time
        # after the ooresults server process has terminated. This prevents the
        # temporary directory from being deleted. We wait until the database file
        # can be deleted.
        for i in range(10):
            try:
                (pathlib.Path(d_name) / "ooresults.sqlite").unlink()
                break
            except OSError:
                time.sleep(1)


@pytest.fixture(scope="session")
def download_dir() -> Iterator[pathlib.Path]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield pathlib.Path(temp_dir)


@pytest.fixture(scope="session")
def driver(download_dir: pathlib.Path) -> Iterator[webdriver.Remote]:
    options = webdriver.FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.helperApps.alwaysAsk.force", False)
    options.set_preference("browser.download.alwaysOpenPanel", False)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.manager.showAlertOnComplete", False)
    options.set_preference("browser.download.dir", str(download_dir))
    options.set_preference("pdfjs.disabled", True)
    options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/pdf,application/xml,text/csv",
    )
    driver: webdriver.Remote = webdriver.Firefox(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def main_page(ooresults_server: subprocess.Popen, driver: webdriver.Remote) -> MainPage:
    # wait until webserver is responding
    for i in range(10):
        try:
            driver.get("https://admin:admin@localhost:8080")
            break
        except WebDriverException:
            time.sleep(1)
    else:
        driver.get("https://admin:admin@localhost:8080")

    assert "ooresults" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "Administration")
    elem.click()
    return MainPage(driver=driver)


def post(url: str, data: dict[str, str]) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    r = requests.post(
        url=url,
        auth=("admin", "admin"),
        verify=False,
        data=data,
    )
    assert r.status_code == 200

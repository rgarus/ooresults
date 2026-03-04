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


import pytest
from selenium.common.exceptions import NoAlertPresentException

from webtests.pageobjects.main_page import MainPage


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # see https://docs.pytest.org/en/6.2.x/example/simple.html#making-test-result-information-available-in-fixtures
    # see https://docs.pytest.org/en/6.2.x/example/simple.html#post-process-test-reports-failures
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when in ("setup", "call") and rep.outcome == "failed":
        if "main_page" in item.fixturenames and "main_page" in item.funcargs:
            main_page: MainPage = item.funcargs["main_page"]

            # close alert popup window if displayed
            try:
                main_page.driver.switch_to.alert.dismiss()
            except NoAlertPresentException:
                pass

            # load main page
            main_page.load()

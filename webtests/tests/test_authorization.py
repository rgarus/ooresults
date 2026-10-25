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


import requests
import urllib3

from webtests.pageobjects.main_page import MainPage


URL = "https://localhost:8080/event/update"
UNAUTHORIZED = (
    "<!DOCTYPE HTML>\n"
    + "<html>\n"
    + "<head>\n"
    + "<title>401 Unauthorized</title>\n"
    + "</head>\n"
    + "<body>\n"
    + "<h1>Unauthorized</h1>\n"
    + "<p>This server could not verify that you are authorized to "
    + "access the document requested. Either you supplied the wrong\n"
    + "credentials (e.g., bad password), or your browser doesn't "
    + "understand how to supply the credentials required.</p>\n"
    + "</body>\n"
    + "</html>\n"
)


def test_if_authorization_header_is_missing_then_status_code_is_401(
    main_page: MainPage,
) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    r = requests.post(
        url=URL,
        verify=False,
    )
    assert r.status_code == 401
    assert r.text == UNAUTHORIZED


def test_if_authorization_header_is_invalid_then_status_code_is_401(
    main_page: MainPage,
) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    r = requests.post(
        url=URL,
        verify=False,
        headers={"Authorization": "Basic !!!"},
    )
    assert r.status_code == 401
    assert r.text == UNAUTHORIZED


def test_if_password_is_incorrect_then_status_code_is_401(
    main_page: MainPage,
) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    r = requests.post(
        url=URL,
        verify=False,
        auth=("admin", "xxxxx"),
    )
    assert r.status_code == 401
    assert r.text == UNAUTHORIZED

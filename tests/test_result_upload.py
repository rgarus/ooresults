# Copyright (C) 2026 Arist Kozhevnikov
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


import configparser
import io
import json
import urllib.parse
from datetime import date
from typing import Any
from typing import Optional
from unittest.mock import Mock
from unittest.mock import patch

import bottle
import pytest
import requests
from lxml import etree
from requests import Response
from requests.structures import CaseInsensitiveDict

from ooresults.handler import entries
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import result_upload
from ooresults.utils.result_upload import Upload
from ooresults.utils.result_upload import UploadAnswer


URL = "http://127.0.0.1:8080/cup_import.php"
POST = "ooresults.utils.result_upload.requests.post"


def target(url: str) -> Upload:
    upload = Upload(config=configparser.ConfigParser())
    upload.url = url
    upload.token = "secret"
    upload.name = "Test Cup"
    return upload


@pytest.fixture
def response() -> Response:
    response = requests.Response()
    response.status_code = 200
    response._content = b""
    response.headers = CaseInsensitiveDict(
        {"Location": "https://www.example.org/cup_import.php"}
    )
    return response


def assert_called(mock_post: Mock) -> None:
    mock_post.assert_called_once_with(
        url=URL,
        data=b"<ResultList/>",
        headers={
            "Content-Type": "application/xml; charset=utf-8",
            "Accept": "application/json",
            "X-Upload-Token": "secret",
        },
        timeout=(10, 60),
        allow_redirects=False,
    )


def test_upload_sends_result_list_with_token(response: Response) -> None:
    response._content = json.dumps(
        {
            "ok": True,
            "message": "52 results received",
            "review_url": "https://www.example.org/cup.php?page=import&id=7",
        }
    ).encode()

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")

    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(
        ok=True,
        message="52 results received",
        review_url="https://www.example.org/cup.php?page=import&id=7",
    )


def test_upload_error_reported_by_server(response: Response) -> None:
    response.status_code = 401
    response._content = json.dumps({"ok": False, "message": "Invalid token"}).encode()

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")
    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(ok=False, message="Invalid token")


def test_upload_is_only_ok_with_http_status_200(response: Response) -> None:
    response.status_code = 500
    response._content = json.dumps({"ok": True, "message": "something"}).encode()

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")
    assert_called(mock_post=mock_post)
    assert answer.ok is False


def test_upload_answer_is_not_json(response: Response) -> None:
    response.status_code = 500
    response._content = b"<html>\n<body>Internal Server Error</body>\n</html>"

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")
    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(
        ok=False,
        message="Unexpected answer from 127.0.0.1 (HTTP 500): <html> <body>Internal Server Error</body> </html>",
    )


def test_upload_does_not_follow_redirects(response: Response) -> None:
    response.status_code = 301
    response._content = json.dumps(
        {
            "ok": True,
            "message": "52 results received",
            "review_url": "https://www.example.org/cup.php?page=import&id=7",
        }
    ).encode()

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")
    assert_called(mock_post=mock_post)
    assert answer.ok is False
    assert "redirects to https://www.example.org/cup_import.php" in answer.message


@pytest.mark.parametrize("review_url", ["javascript:alert(1)", 42, ""])
def test_upload_invalid_review_url_is_ignored(
    response: Response, review_url: Any
) -> None:
    response.status_code = 200
    response._content = json.dumps(
        {"ok": True, "message": "received", "review_url": review_url}
    ).encode()

    with patch(target=POST, autospec=True, return_value=response) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")
    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(ok=True, message="received", review_url=None)


def test_upload_connection_timeout() -> None:
    with patch(
        target=POST, autospec=True, side_effect=requests.ConnectTimeout()
    ) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")

    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(
        ok=False, message="No answer from 127.0.0.1 (timeout)."
    )


def test_upload_read_timeout() -> None:
    with patch(
        target=POST, autospec=True, side_effect=requests.ReadTimeout()
    ) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")

    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(
        ok=False, message="No answer from 127.0.0.1 (timeout)."
    )


def test_upload_connection_refused() -> None:
    with patch(
        target=POST, autospec=True, side_effect=requests.ConnectionError()
    ) as mock_post:
        answer = target(url=URL).upload(content=b"<ResultList/>")

    assert_called(mock_post=mock_post)
    assert answer == UploadAnswer(
        ok=False,
        message="Cannot connect to 127.0.0.1. Please check the internet connection.",
    )


#
# handler /entry/upload
#

EVENT = EventType(
    id=3,
    name="9. Munich O-Cup 2026",
    date=date(year=2026, month=11, day=8),
    key=None,
    publish=False,
    series=None,
    fields=[],
)


def post_upload(event_id: str) -> Any:
    body = urllib.parse.urlencode({"event_id": event_id}).encode()
    bottle.request.bind(
        {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/entry/upload",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "CONTENT_LENGTH": str(len(body)),
            "wsgi.input": io.BytesIO(body),
        }
    )
    return entries.post_upload()


def test_handler_upload_not_configured() -> None:
    with patch.object(result_upload, "upload", None):
        response = post_upload(event_id="3")
    assert isinstance(response, bottle.HTTPResponse)
    assert response.status_code == 409


def test_handler_upload_without_selected_event() -> None:
    with patch.object(result_upload, "upload", target(url="https://www.example.org")):
        response = post_upload(event_id="null")
    assert isinstance(response, bottle.HTTPResponse)
    assert response.status_code == 409
    assert response.body == "No event selected"


def test_handler_upload_event_deleted() -> None:
    with (
        patch.object(result_upload, "upload", target(url="https://www.example.org")),
        patch.object(
            entries.model.results,
            "event_class_results",
            side_effect=EventNotFoundError,
        ),
    ):
        response = post_upload(event_id="3")
    assert isinstance(response, bottle.HTTPResponse)
    assert response.status_code == 409
    assert response.body == "Event deleted"


def test_handler_upload_sends_iof_result_list() -> None:
    sent: dict[str, Optional[bytes]] = {"content": None}

    def fake_upload(content: bytes) -> UploadAnswer:
        sent["content"] = content
        return UploadAnswer(
            ok=True, message="52 results received", review_url="https://x.org/r"
        )

    with (
        patch.object(result_upload, "upload", target(url="https://www.example.org")),
        patch.object(
            entries.model.results,
            "event_class_results",
            return_value=(EVENT, []),
        ) as event_class_results,
        patch.object(result_upload.upload, "upload", side_effect=fake_upload),
    ):
        response = post_upload(event_id="3")

    event_class_results.assert_called_once_with(event_id=3)
    assert json.loads(response) == {
        "ok": True,
        "message": "52 results received",
        "review_url": "https://x.org/r",
    }
    assert sent["content"] is not None
    root = etree.fromstring(sent["content"])
    ns = {"iof": "http://www.orienteering.org/datastandard/3.0"}
    assert root.tag == "{http://www.orienteering.org/datastandard/3.0}ResultList"
    assert root.findtext("iof:Event/iof:Name", namespaces=ns) == "9. Munich O-Cup 2026"
    assert (
        root.findtext("iof:Event/iof:StartTime/iof:Date", namespaces=ns) == "2026-11-08"
    )

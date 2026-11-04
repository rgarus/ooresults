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


import http.server
import io
import json
import socket
import threading
import time
import urllib.parse
from collections.abc import Iterator
from datetime import date
from typing import Any
from typing import Optional
from unittest.mock import patch

import bottle
import pytest
from lxml import etree

from ooresults.handler import entries
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import EventNotFoundError
from ooresults.utils import result_upload
from ooresults.utils.result_upload import UploadAnswer
from ooresults.utils.result_upload import UploadTarget


class Remote:
    """Answer and received requests of the test server."""

    def __init__(self) -> None:
        self.status = 200
        self.headers: dict[str, str] = {"Content-Type": "application/json"}
        self.body = b'{"ok": true, "message": "received"}'
        self.delay = 0.0
        self.requests: list[dict[str, Any]] = []


class QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address) -> None:
        pass


@pytest.fixture
def remote() -> Iterator[tuple[str, Remote]]:
    r = Remote()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", 0))
            r.requests.append(
                {
                    "path": self.path,
                    "headers": dict(self.headers),
                    "body": self.rfile.read(length),
                }
            )
            time.sleep(r.delay)
            self.send_response(r.status)
            for key, value in r.headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(r.body)))
            self.end_headers()
            self.wfile.write(r.body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = QuietServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/cup_import.php", r
    server.shutdown()
    server.server_close()


def target(url: str) -> UploadTarget:
    return UploadTarget(url=url, token="secret", name="Test Cup")


def test_upload_sends_result_list_with_token(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.body = json.dumps(
        {
            "ok": True,
            "message": "52 results received",
            "review_url": "https://www.example.org/cup.php?page=import&id=7",
        }
    ).encode()

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))

    assert answer == UploadAnswer(
        ok=True,
        message="52 results received",
        review_url="https://www.example.org/cup.php?page=import&id=7",
    )
    assert len(r.requests) == 1
    assert r.requests[0]["path"] == "/cup_import.php"
    assert r.requests[0]["body"] == b"<ResultList/>"
    assert r.requests[0]["headers"]["X-Upload-Token"] == "secret"
    assert r.requests[0]["headers"]["Content-Type"] == "application/xml; charset=utf-8"


def test_upload_error_reported_by_server(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.status = 401
    r.body = json.dumps({"ok": False, "message": "Invalid token"}).encode()

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer == UploadAnswer(ok=False, message="Invalid token")


def test_upload_is_only_ok_with_http_status_200(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.status = 500
    r.body = json.dumps({"ok": True, "message": "something"}).encode()

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer.ok is False


def test_upload_answer_is_not_json(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.status = 500
    r.headers = {"Content-Type": "text/html"}
    r.body = b"<html>\n<body>Internal  Server Error</body>\n</html>"

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer == UploadAnswer(
        ok=False,
        message="Unexpected answer from 127.0.0.1 (HTTP 500): <html> <body>Internal Server Error</body> </html>",
    )


def test_upload_does_not_follow_redirects(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.status = 301
    r.headers = {"Location": "https://www.example.org/cup_import.php"}
    r.body = b""

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer.ok is False
    assert "redirects to https://www.example.org/cup_import.php" in answer.message
    assert len(r.requests) == 1


@pytest.mark.parametrize("review_url", ["javascript:alert(1)", 42, ""])
def test_upload_invalid_review_url_is_ignored(
    remote: tuple[str, Remote], review_url: Any
) -> None:
    url, r = remote
    r.body = json.dumps(
        {"ok": True, "message": "received", "review_url": review_url}
    ).encode()

    answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer == UploadAnswer(ok=True, message="received", review_url=None)


def test_upload_timeout(remote: tuple[str, Remote]) -> None:
    url, r = remote
    r.delay = 1.0

    with patch.object(result_upload, "TIMEOUT", (1, 0.2)):
        answer = result_upload.upload(content=b"<ResultList/>", target=target(url))
    assert answer == UploadAnswer(
        ok=False, message="No answer from 127.0.0.1 (timeout)."
    )


def test_upload_connection_refused() -> None:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    # nobody listens on port now

    answer = result_upload.upload(
        content=b"<ResultList/>",
        target=target(f"http://127.0.0.1:{port}/cup_import.php"),
    )
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
    with patch.object(result_upload, "target", None):
        response = post_upload(event_id="3")
    assert isinstance(response, bottle.HTTPResponse)
    assert response.status_code == 409


def test_handler_upload_without_selected_event() -> None:
    with patch.object(result_upload, "target", target("https://www.example.org")):
        response = post_upload(event_id="null")
    assert isinstance(response, bottle.HTTPResponse)
    assert response.status_code == 409
    assert response.body == "No event selected"


def test_handler_upload_event_deleted() -> None:
    with (
        patch.object(result_upload, "target", target("https://www.example.org")),
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

    def fake_upload(content: bytes, target: UploadTarget) -> UploadAnswer:
        sent["content"] = content
        return UploadAnswer(
            ok=True, message="52 results received", review_url="https://x.org/r"
        )

    with (
        patch.object(result_upload, "target", target("https://www.example.org")),
        patch.object(
            entries.model.results,
            "event_class_results",
            return_value=(EVENT, []),
        ) as event_class_results,
        patch.object(result_upload, "upload", side_effect=fake_upload),
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

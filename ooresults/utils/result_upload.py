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


"""Upload of an IOF 3.0 ResultList to a remote server.

The receiving server (e.g. the website of a cup series) gets a POST request
with the ResultList as body and the token of the [Upload] section of the
configuration file in the header "X-Upload-Token". It answers with a JSON
object:

    {"ok": true, "message": "...", "review_url": "https://..."}

"review_url" is optional. It is shown as a link, for example to a page where
the uploaded results are checked before they are taken over.
"""


import configparser
import dataclasses
import logging
from typing import Optional
from urllib.parse import urlsplit

import requests


TOKEN_HEADER = "X-Upload-Token"

# (connect timeout, read timeout) in seconds
TIMEOUT = (10, 60)

MAX_MESSAGE_LENGTH = 500


@dataclasses.dataclass(frozen=True)
class UploadAnswer:
    ok: bool
    message: str
    review_url: Optional[str] = None


class Upload:
    def __init__(self, config: configparser.ConfigParser) -> None:
        self.url = ""
        self.token = ""
        self.name = ""
        self._read_upload_section(config=config)

    def _read_upload_section(self, config: configparser.ConfigParser) -> None:
        #  [Upload]  (optional)
        #  url = https://www.example.org/import.php
        #  token = secret
        #  name = Example Cup
        #
        if not config.has_section("Upload"):
            return None

        # raw: a token may contain "%" characters
        self.url = config.get("Upload", "url", raw=True, fallback="").strip()
        self.token = config.get("Upload", "token", raw=True, fallback="").strip()
        self.name = config.get("Upload", "name", raw=True, fallback="").strip()
        if self.url == "":
            return None

        try:
            parts = urlsplit(self.url)
            scheme, hostname = parts.scheme, parts.hostname
        except ValueError:
            scheme, hostname = "", None
        if hostname is None or scheme not in ("http", "https"):
            raise RuntimeError(
                "Value of 'url' in section [Upload] must be an address starting with 'https://'"
            )
        if scheme == "http" and hostname not in ("localhost", "127.0.0.1", "::1"):
            raise RuntimeError(
                "Value of 'url' in section [Upload] must start with 'https://' (the token must not be sent unencrypted)"
            )
        if self.token == "":
            raise RuntimeError("Section [Upload] requires a value for 'token'")
        if not self.name:
            self.name = hostname
        return None

    def upload(self, content: bytes) -> UploadAnswer:
        """Send content (an IOF 3.0 ResultList) to the upload target."""
        host = urlsplit(self.url).hostname
        logging.info(f"Upload of results to {self.url} ({len(content)} bytes)")
        try:
            response = requests.post(
                url=self.url,
                data=content,
                headers={
                    "Content-Type": "application/xml; charset=utf-8",
                    "Accept": "application/json",
                    TOKEN_HEADER: self.token,
                },
                timeout=TIMEOUT,
                # a redirect would turn the POST request into a GET request
                # or send the token to another server
                allow_redirects=False,
            )
        except requests.exceptions.Timeout:
            answer = UploadAnswer(ok=False, message=f"No answer from {host} (timeout).")
        except requests.exceptions.SSLError as e:
            answer = UploadAnswer(ok=False, message=f"TLS error for {host}: {e}")
        except requests.exceptions.ConnectionError:
            answer = UploadAnswer(
                ok=False,
                message=f"Cannot connect to {host}. Please check the internet connection.",
            )
        except requests.exceptions.RequestException as e:
            answer = UploadAnswer(ok=False, message=f"Upload failed: {e}")
        else:
            answer = self._evaluate(response=response, host=host)

        logging.info(f"Upload of results: ok={answer.ok}, message={answer.message!r}")
        return answer

    def _evaluate(
        self, response: requests.Response, host: Optional[str]
    ) -> UploadAnswer:
        if response.is_redirect:
            location = response.headers.get("Location", "")
            return UploadAnswer(
                ok=False,
                message=f"{host} redirects to {location}. Please correct the url in the [Upload] section of config.ini.",
            )

        try:
            data = response.json()
        except ValueError:
            data = None

        if not isinstance(data, dict):
            text = " ".join(response.text.split())[:200]
            return UploadAnswer(
                ok=False,
                message=f"Unexpected answer from {host} (HTTP {response.status_code}): {text}",
            )

        message = data.get("message")
        if not isinstance(message, str) or message == "":
            message = f"HTTP {response.status_code}"
        message = message[:MAX_MESSAGE_LENGTH]

        review_url = data.get("review_url")
        if not isinstance(review_url, str) or urlsplit(review_url).scheme not in (
            "http",
            "https",
        ):
            review_url = None

        return UploadAnswer(
            ok=data.get("ok") is True and response.status_code == 200,
            message=message,
            review_url=review_url,
        )


upload: Optional[Upload] = None

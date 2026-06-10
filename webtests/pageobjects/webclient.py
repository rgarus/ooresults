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

import bz2
import json
import ssl
import threading
from queue import Queue
from typing import Any
from typing import Optional

from websocket import WebSocketApp


class WebSocketClient(threading.Thread):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8081,
        key: str = "local",
        ssl_cert: Optional[str] = None,
        ssl_verify: bool = False,
    ) -> None:
        super().__init__()
        self.daemon = True
        self.host = host
        self.port = port
        self.key = key
        self.ssl_cert = ssl_cert
        self.ssl_verify = ssl_verify
        self.wsapp: Optional[WebSocketApp] = None
        self.opened = False
        self.reconnect = True
        self.queue: Queue[str | bytes] = Queue()

    def run(self) -> None:
        headers = {
            "Content-Type": "application/octet-stream",
            "X-Event-Key": self.key,
            "X-Suffix": ".json",
        }
        sslopt: dict[str, Any] = {"cert_reqs": ssl.CERT_REQUIRED}

        if not self.ssl_verify:
            # disable ssl verification: sslopt = {'cert_reqs': ssl.CERT_NONE}
            # disable hostname verification: sslopt = {'check_hostname': False}
            sslopt["cert_reqs"] = ssl.CERT_NONE
        if self.ssl_cert is not None:
            sslopt["ca_certs"] = self.ssl_cert

        uri = f"wss://{self.host}:{str(self.port)}/cardreader"
        while self.reconnect:
            print(f"Trying to connect to {uri} ...")
            self.wsapp = WebSocketApp(
                url=uri,
                header=headers,
                on_open=self.on_open,
                on_close=self.on_close,
                on_message=self.on_message,
                on_error=self.on_error,
            )
            self.wsapp.run_forever(sslopt=sslopt)

    def send_and_receive(self, item: dict, timeout: Optional[int] = None) -> dict:
        self.clear()
        data = bz2.compress(json.dumps(item).encode())
        self.send(data)
        return self.receive(timeout=timeout)

    def send(self, data: bytes) -> None:
        if self.wsapp and self.opened:
            self.wsapp.send(data, opcode=2)
        else:
            raise RuntimeError("Not connected to server")

    def receive(self, timeout: Optional[int] = None) -> dict:
        if self.opened:
            return json.loads(self.queue.get(timeout=timeout))
        else:
            return {}

    def clear(self) -> None:
        while not self.queue.empty():
            self.queue.get()

    def on_close(self, wsapp: WebSocketApp, close_status_code, close_msg) -> None:
        self.opened = False

    def on_open(self, wsapp: WebSocketApp) -> None:
        self.opened = True

    def on_message(self, wsapp: WebSocketApp, message: str | bytes) -> None:
        self.queue.put(message)

    def on_error(self, wsapp: WebSocketApp, message: str | bytes) -> None:
        print(message)

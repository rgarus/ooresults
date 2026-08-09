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


import secrets
import threading
import time


class Credentials:
    lock = threading.Lock()

    def __init__(self) -> None:
        self.store: dict[str, float] = {}

    def create_token(self) -> str:
        new_token = secrets.token_hex(32)
        with self.lock:
            # remove expired tokens
            for token, creation_time in self.store.copy().items():
                if creation_time + 60 < time.time():
                    del self.store[token]
            # add new created token
            self.store[new_token] = time.time()
        return new_token

    def check_token(self, token: str) -> bool:
        with self.lock:
            # check if token exist and is not expired
            creation_time = self.store.get(token, 0)
            return creation_time + 60 >= time.time()


credentials = Credentials()

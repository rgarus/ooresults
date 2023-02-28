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


import json
import pathlib
import threading
from typing import Dict
from typing import Optional

import jsonschema


SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["username", "password"],
        "additionalProperties": False,
    },
}


class Users:
    sema = threading.Semaphore()
    path: Optional[pathlib.Path] = None
    users: Dict[str, str] = {}

    @classmethod
    def check(cls, username: str, password: str) -> bool:
        with cls.sema:
            return username in cls.users and cls.users[username] == password

    @classmethod
    def create_default_file_if_not_exist(cls) -> None:
        users = [
            {
                "username": "admin",
                "password": "admin",
            }
        ]
        if cls.path and not cls.path.exists():
            cls.path.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.path, "w") as f:
                json.dump(users, f, indent=4)

    @classmethod
    def update(cls, path: Optional[pathlib.Path] = None) -> None:
        if path:
            cls.path = path

        if cls.path:
            cls.create_default_file_if_not_exist()

            with open(cls.path) as f:
                data = json.load(f)
            jsonschema.validate(instance=data, schema=SCHEMA)
            with cls.sema:
                cls.users = {}
                for user in data:
                    cls.users[user["username"]] = user["password"]

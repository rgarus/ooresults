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
import tempfile

from ooresults import user


def test_default_values_if_file_not_exist():
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "users.json"

        user.Users.update(path=path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)
        assert data == [{"username": "admin", "password": "admin"}]
        assert user.Users.path == path
        assert user.Users.users == {"admin": "admin"}


def test_update_values_if_file_exist():
    users = [
        {"username": "a", "password": "x"},
        {"username": "b", "password": "y"},
        {"username": "c", "password": "z"},
    ]
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "users.json"
        with open(path, "w") as f:
            f.write(json.dumps(users))

        user.Users.update(path=path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)
        assert data == users
        assert user.Users.path == path
        assert user.Users.users == {"a": "x", "b": "y", "c": "z"}


def test_check_username_and_password():
    user.Users.users = {
        "abc": "p1",
        "def": "p2",
        "ghi": "p3",
    }
    assert user.Users.check("abc", "p1")
    assert user.Users.check("def", "p2")
    assert user.Users.check("ghi", "p3")
    assert not user.Users.check("abc", "p2")
    assert not user.Users.check("abc", "p3")
    assert not user.Users.check("xxx", "pp")

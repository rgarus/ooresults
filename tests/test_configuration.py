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
import tempfile
from unittest.mock import patch

import pytest

from ooresults import configuration


def test_configuration_create_default_config_if_not_exists():
    with tempfile.TemporaryDirectory() as hd:
        home = pathlib.Path(hd)

        def my_home() -> pathlib.Path:
            return home

        with patch.object(pathlib.Path, "home", my_home):
            c = configuration.Config(path=home / ".ooresults")
            assert c.ssl_cert == home / ".ooresults" / "cert" / "cert.pem"
            assert c.ssl_key == home / ".ooresults" / "cert" / "privkey.pem"
            assert c.demo_reader is False
            assert c.import_stream is False

            assert c.ssl_cert.exists()
            assert c.ssl_key.exists()
            assert (home / ".ooresults" / "config.ini").exists()


def test_configuration_cert_files_are_created_in_home():
    with tempfile.TemporaryDirectory() as td:
        with tempfile.TemporaryDirectory() as hd:
            temp = pathlib.Path(td)
            home = pathlib.Path(hd)

            def my_home() -> pathlib.Path:
                return home

            with patch.object(pathlib.Path, "home", my_home):
                c = configuration.Config(path=temp)
                assert c.ssl_cert == home / ".ooresults" / "cert" / "cert.pem"
                assert c.ssl_key == home / ".ooresults" / "cert" / "privkey.pem"
                assert c.demo_reader is False
                assert c.import_stream is False

                assert c.ssl_cert.exists()
                assert c.ssl_key.exists()
                assert c.ssl_cert.stat().st_size > 100
                assert c.ssl_key.stat().st_size > 100
                assert (temp / "config.ini").exists()


def test_configuration_cert_files_are_only_created_if_not_exist():
    with tempfile.TemporaryDirectory() as td:
        with tempfile.TemporaryDirectory() as hd:
            temp = pathlib.Path(td)
            home = pathlib.Path(hd)

            def my_home() -> pathlib.Path:
                return home

            ssl_cert = home / ".ooresults" / "cert" / "cert.pem"
            ssl_key = home / ".ooresults" / "cert" / "privkey.pem"
            ssl_cert.parent.mkdir(parents=True, exist_ok=True)
            ssl_cert.touch()
            ssl_key.touch()

            with patch.object(pathlib.Path, "home", my_home):
                c = configuration.Config(path=temp)
                assert ssl_cert.stat().st_size == 0
                assert ssl_key.stat().st_size == 0
                assert c.ssl_cert == ssl_cert
                assert c.ssl_key == ssl_key


def test_configuration_cert_files_are_not_created_if_defined_in_config():
    with tempfile.TemporaryDirectory() as td:
        with tempfile.TemporaryDirectory() as hd:
            temp = pathlib.Path(td)
            home = pathlib.Path(hd)

            def my_home() -> pathlib.Path:
                return home

            ssl_cert = temp / "cert.pem"
            ssl_key = temp / "privkey.pem"
            ssl_cert.touch()
            ssl_key.touch()

            config_file = temp / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")
                f.write(f"ssl_cert = {str(ssl_cert)}\n")
                f.write(f"ssl_key = {str(ssl_key)}\n")

            with patch.object(pathlib.Path, "home", my_home):
                c = configuration.Config(path=temp)

                assert not (home / ".ooresults" / "cert" / "cert.pem").exists()
                assert not (home / ".ooresults" / "cert" / "privkey.pem").exists()
                assert not (home / "config.ini").exists()

                assert c.ssl_cert == ssl_cert
                assert c.ssl_key == ssl_key
                assert c.ssl_cert.stat().st_size == 0
                assert c.ssl_key.stat().st_size == 0


def test_configuration_exception_if_cert_files_defined_but_not_found():
    with tempfile.TemporaryDirectory() as td:
        with tempfile.TemporaryDirectory() as hd:
            temp = pathlib.Path(td)
            home = pathlib.Path(hd)

            def my_home() -> pathlib.Path:
                return home

            ssl_cert = temp / "cert.pem"
            ssl_key = temp / "privkey.pem"

            config_file = temp / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")
                f.write(f"ssl_cert = {str(ssl_cert)}\n")
                f.write(f"ssl_key = {str(ssl_key)}\n")

            with patch.object(pathlib.Path, "home", my_home):
                with pytest.raises(
                    expected_exception=FileNotFoundError,
                    match=f"Certificate file '{ssl_cert}' not found",
                ):
                    c = configuration.Config(path=temp)

                assert not (home / ".ooresults" / "cert" / "cert.pem").exists()
                assert not (home / ".ooresults" / "cert" / "privkey.pem").exists()
                assert not (home / "config.ini").exists()


def test_configuration_demo_reader_default_is_false():
    with tempfile.TemporaryDirectory() as td:
        home = pathlib.Path(td)

        def my_home() -> pathlib.Path:
            return home

        with patch.object(pathlib.Path, "home", my_home):
            config_file = home / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")

            c = configuration.Config(path=home)
            assert c.demo_reader is False


def test_configuration_import_stream_default_is_false():
    with tempfile.TemporaryDirectory() as td:
        home = pathlib.Path(td)

        def my_home() -> pathlib.Path:
            return home

        with patch.object(pathlib.Path, "home", my_home):
            config_file = home / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")

            c = configuration.Config(path=home)
            assert c.import_stream is False


def test_configuration_config_file_is_read_if_exists_1():
    with tempfile.TemporaryDirectory() as td:
        home = pathlib.Path(td)

        def my_home() -> pathlib.Path:
            return home

        with patch.object(pathlib.Path, "home", my_home):
            config_file = home / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")
                f.write("demo_reader = off\n")
                f.write("import_stream = on\n")

            c = configuration.Config(path=home)
            assert c.demo_reader is False
            assert c.import_stream is True


def test_configuration_config_file_is_read_if_exists_2():
    with tempfile.TemporaryDirectory() as td:
        home = pathlib.Path(td)

        def my_home() -> pathlib.Path:
            return home

        with patch.object(pathlib.Path, "home", my_home):
            config_file = home / "config.ini"
            with open(config_file, "w") as f:
                f.write("[Server]\n")
                f.write("demo_reader = on\n")
                f.write("import_stream = off\n")

            c = configuration.Config(path=home)
            assert c.demo_reader is True
            assert c.import_stream is False

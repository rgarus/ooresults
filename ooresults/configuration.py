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


import configparser
import pathlib
from typing import List
from typing import Optional

from OpenSSL import crypto


class Config:
    def __init__(self, path: pathlib.Path):
        # config file
        #
        #  [Server]
        #  ssl_cert = cert/cert.pem
        #  ssl_key = cert/privkey.pem
        #  demo_reader = off
        #

        self.config_file = path / "config.ini"
        self.ssl_cert = pathlib.Path.home() / ".ooresults" / "cert" / "cert.pem"
        self.ssl_key = pathlib.Path.home() / ".ooresults" / "cert" / "privkey.pem"
        self.demo_reader = False

        config = configparser.ConfigParser()
        if self.config_file.exists():
            config.read(self.config_file)
        else:
            config["Server"] = {
                "ssl_cert": "",
                "ssl_key": "",
                "demo_reader": "off",
            }
            config["Cardreader"] = {
                "host": "127.0.0.1",
                "ssl_verify": "false",
                "key": "local",
                "serial_number": "",
            }
            self.write_config_file(config=config)

        ssl_cert = config.get("Server", "ssl_cert", fallback=None)
        ssl_key = config.get("Server", "ssl_key", fallback=None)

        if ssl_cert or ssl_key:
            if pathlib.Path(ssl_cert).exists() and pathlib.Path(ssl_cert).is_file():
                self.ssl_cert = pathlib.Path(ssl_cert)
            else:
                raise FileNotFoundError(f"Certificate file '{ssl_cert}' not found")
            if pathlib.Path(ssl_key).exists() and pathlib.Path(ssl_key).is_file():
                self.ssl_key = pathlib.Path(ssl_key)
            else:
                raise FileNotFoundError(f"Private key file '{ssl_key}' not found")

        try:
            self.demo_reader = config.getboolean(
                "Server", "demo_reader", fallback=False
            )
        except ValueError:
            raise RuntimeError(
                "Allowed values for 'demo_reader' are 'true', 'false', 'on', 'off', 'yes', 'no'"
            )

        # create cert files for localhost if files not exist
        if (
            not pathlib.Path(self.ssl_cert).exists()
            or not pathlib.Path(self.ssl_key).exists()
        ):
            self.create_self_signed_cert()

    def write_config_file(self, config: configparser.ConfigParser) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            config.write(f)

    def create_self_signed_cert(self) -> None:
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "DE"
        cert.get_subject().O = "ooresults"
        cert.get_subject().OU = "ooresults"
        cert.get_subject().CN = "localhost"
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(20 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, "sha1")

        if not self.ssl_cert.exists():
            self.ssl_cert.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ssl_cert, "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        if not self.ssl_key.exists():
            self.ssl_key.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ssl_key, "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

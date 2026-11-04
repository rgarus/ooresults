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
import datetime
import pathlib
from typing import Optional
from urllib.parse import urlsplit

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ooresults.utils.result_upload import UploadTarget


class Config:
    def __init__(self, path: pathlib.Path):
        # config file
        #
        #  [Server]
        #  ssl_cert = cert/cert.pem
        #  ssl_key = cert/privkey.pem
        #  demo_reader = off
        #  import_stream = off
        #
        #  [Upload]  (optional)
        #  url = https://www.example.org/import.php
        #  token = secret
        #  name = Example Cup
        #

        self.config_file = path / "config.ini"
        self.ssl_cert = pathlib.Path.home() / ".ooresults" / "cert" / "cert.pem"
        self.ssl_key = pathlib.Path.home() / ".ooresults" / "cert" / "privkey.pem"
        self.demo_reader = False
        self.import_stream = False
        self.upload: Optional[UploadTarget] = None

        config = configparser.ConfigParser()
        if self.config_file.exists():
            config.read(self.config_file)
        else:
            config["Server"] = {
                "ssl_cert": "",
                "ssl_key": "",
                "demo_reader": "off",
                "import_stream": "off",
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
            if ssl_cert is not None and pathlib.Path(ssl_cert).is_file():
                self.ssl_cert = pathlib.Path(ssl_cert)
            else:
                raise FileNotFoundError(f"Certificate file '{ssl_cert}' not found")
            if ssl_key is not None and pathlib.Path(ssl_key).is_file():
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

        try:
            self.import_stream = config.getboolean(
                "Server", "import_stream", fallback=False
            )
        except ValueError:
            raise RuntimeError(
                "Allowed values for 'import_stream' are 'true', 'false', 'on', 'off', 'yes', 'no'"
            )

        self.upload = self.read_upload_section(config=config)

        # create cert files for localhost if files not exist
        if (
            not pathlib.Path(self.ssl_cert).exists()
            or not pathlib.Path(self.ssl_key).exists()
        ):
            self.create_self_signed_cert()

    @staticmethod
    def read_upload_section(
        config: configparser.ConfigParser,
    ) -> Optional[UploadTarget]:
        if not config.has_section("Upload"):
            return None

        # raw: a token may contain "%" characters
        url = config.get("Upload", "url", raw=True, fallback="").strip()
        token = config.get("Upload", "token", raw=True, fallback="").strip()
        name = config.get("Upload", "name", raw=True, fallback="").strip()
        if url == "":
            return None

        try:
            parts = urlsplit(url)
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
        if token == "":
            raise RuntimeError("Section [Upload] requires a value for 'token'")

        return UploadTarget(url=url, token=token, name=name or hostname)

    def write_config_file(self, config: configparser.ConfigParser) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            config.write(f)

    def create_self_signed_cert(self) -> None:
        # Generate private key
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        # Write key unencrypted to disk
        self.ssl_key.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ssl_key, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # For a self-signed certificate the subject and issuer are always the same
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ooresults"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "ooresults"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ]
        )
        # Create and sign certificate
        now = datetime.datetime.now(datetime.timezone.utc)
        expiry = now + datetime.timedelta(days=20 * 365)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(expiry)
            .sign(key, hashes.SHA256())
        )
        # Write certificate to disk
        self.ssl_cert.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ssl_cert, "wb") as f:
            f.write(cert.public_bytes(encoding=serialization.Encoding.PEM))

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


import argparse
import configparser
import datetime
import pathlib
import json
import time
import threading
import bz2
import ssl
import queue
from typing import Dict
from typing import Optional

import websocket
import jsonschema
import sireader
import serial.tools.list_ports


#
# ConfigFile:
#
#  [Server]
#  ssl_cert = cert/cert.pem
#  ssl_key = cert/privkey.pem
#
#  [Cardreader]
#  host = localhost
#  ssl_cert = cert/cert.pem
#  ssl_verify = true
#  key = 4711
#  serial_number =
#


class WebSocketClient(threading.Thread):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8081,
        key: str = "",
        ssl_cert="cert/cert.pem",
        ssl_verify: bool = True,
    ):
        super().__init__()
        self.daemon = True
        self.host = host
        self.port = port
        self.key = key
        self.ssl_cert = ssl_cert
        self.ssl_verify = ssl_verify
        self.ws = None
        self.opened = False
        self.queue = queue.Queue()
        self.entry_type = "readerDisconnected"
        self.entry_time = datetime.datetime.now()
        self.card = None

    def run(self):
        headers = {
            "Content-Type": "application/octet-stream",
            "X-Event-Key": self.key,
            "X-Suffix": ".json",
        }
        sslopt = {"cert_reqs": ssl.CERT_REQUIRED}

        if not self.ssl_verify:
            # disable ssl verification: sslopt = {'cert_reqs': ssl.CERT_NONE}
            # disable hostname verification: sslopt = {'check_hostname': False}
            sslopt["cert_reqs"] = ssl.CERT_NONE
        if self.ssl_cert is not None:
            sslopt["ca_certs"] = self.ssl_cert

        uri = f"wss://{self.host}:{str(self.port)}/cardreader"
        while True:
            print(f"Trying to connect to {uri} ...")
            self.ws = websocket.WebSocketApp(
                url=uri,
                header=headers,
                on_open=self.on_open,
                on_close=self.on_close,
                on_message=self.on_message,
                on_error=self.on_error,
            )
            self.ws.run_forever(sslopt=sslopt)
            time.sleep(5)

    def set_state(
        self, entry_type: str, entry_time: datetime.datetime, card: Optional[str] = None
    ) -> Dict:
        self.entry_type = entry_type
        self.entry_time = entry_time
        self.card = card
        # send a cardreader state message
        item = {
            "entryType": self.entry_type,
            "entryTime": self.entry_time.astimezone().isoformat(),
        }
        if self.card is not None:
            item["controlCard"] = self.card
        return self.send_and_receive(item=item)

    def send_and_receive(self, item: Dict, timeout: Optional[int] = None) -> Dict:
        self.clear()
        data = bz2.compress(json.dumps(item).encode())
        self.send(data)
        return self.receive(timeout=timeout)

    def send(self, data: bytes) -> None:
        if self.opened:
            self.ws.send(data, opcode=2)
        else:
            print("Not connected to server - could not send data")

    def receive(self, timeout: Optional[int] = None) -> Dict:
        if self.opened:
            return json.loads(self.queue.get(timeout=timeout))
        else:
            return {}

    def clear(self) -> None:
        while not self.queue.empty():
            self.queue.get()

    def on_close(self, wsapp, close_status_code, close_msg):
        if self.opened:
            print("Connection closed")
        self.opened = False

    def on_open(self, wsapp):
        if not self.opened:
            print("Connection established")
            self.opened = True
            item = {
                "entryType": self.entry_type,
                "entryTime": self.entry_time.astimezone().isoformat(),
            }
            data = bz2.compress(json.dumps(item).encode())
            self.send(data=data)

    def on_message(self, wsapp, message):
        self.queue.put(message)

    def on_error(self, wsapp, message):
        print(message)


class Cardreader:
    data_path = (
        pathlib.Path(__file__).resolve().parent / "schema" / "cardreader_log.json"
    )
    with open(data_path, "r") as f:
        schema_cardreader_log = json.loads(f.read())

    def __init__(self, webSocketClient: WebSocketClient, serial_number: str = ""):
        self.webSocketClient = webSocketClient
        self.serial_number = serial_number

    def convert(self, card_type: str, card_data: Dict) -> Dict:
        item = {
            "entryType": "cardRead",
            "entryTime": datetime.datetime.now().astimezone().isoformat(),
            "cardType": card_type,
            "controlCard": str(card_data["card_number"]),
        }

        if card_data.get("start", None) is not None:
            item["startTime"] = card_data["start"].astimezone().isoformat()
        if card_data.get("finish", None) is not None:
            item["finishTime"] = card_data["finish"].astimezone().isoformat()
        if card_data.get("check", None) is not None:
            item["checkTime"] = card_data["check"].astimezone().isoformat()
        if card_data.get("clear", None) is not None:
            item["clearTime"] = card_data["clear"].astimezone().isoformat()

        item["punches"] = []
        for p in card_data["punches"]:
            item["punches"].append(
                {"controlCode": str(p[0]), "punchTime": p[1].astimezone().isoformat()}
            )

        return item

    def protocol(self, item: Dict) -> None:
        date_str = datetime.date.today().isoformat()
        with open(f"cardreader-{date_str}.log", "a") as f:
            f.write(json.dumps(item) + "\n")

    def connect(self) -> sireader.SIReaderReadout:
        errors = ""
        for port in serial.tools.list_ports.grep("sportident"):
            try:
                si = sireader.SIReaderReadout(port.device)
                if not self.serial_number or self.serial_number == port.serial_number:
                    print(f"SI Reader found, serial number: {port.serial_number}")
                    return si
                else:
                    print(f"SI Reader found, but serial number: {port.serial_number}")

            except (sireader.SIReaderException, sireader.SIReaderTimeout) as msg:
                errors += f"port: {port.device}: {msg}\n"
        else:
            errors = "No SI Reader found" if errors == "" else errors
        raise sireader.SIReaderException(
            f"No SI Reader found. Possible reasons: {errors}"
        )

    def reader(self) -> None:
        # connect to base station, the station is automatically detected,
        # if this does not work, give the path to the port as an argument
        # see the pyserial documentation for further information.
        si = self.connect()

        # check extended protocol mode
        extended_protocol = True
        try:
            si.poll_sicard()
        except sireader.SIReaderException:
            extended_protocol = False
            # change to extended protocol mode
            si.set_extended_protocol(True)

        try:
            r = self.webSocketClient.set_state(
                entry_type="readerConnected",
                entry_time=datetime.datetime.now(),
            )

            while True:
                # wait for a card to be inserted into the reader
                while not si.poll_sicard() or si.sicard is None:
                    time.sleep(0.2)

                try:
                    # some properties are now set
                    card_number = si.sicard  #  8320666
                    card_type = si.cardtype  #  'SI10'
                    self.webSocketClient.set_state(
                        entry_type="cardInserted",
                        entry_time=datetime.datetime.now(),
                        card=str(si.sicard),
                    )

                    # read out card data
                    #
                    # {'card_number': 219412,
                    #  'start': datetime.datetime(2021, 5, 18, 16, 31, 19),
                    #  'finish': datetime.datetime(2021, 5, 18, 16, 31, 50),
                    #  'check': datetime.datetime(2021, 5, 18, 16, 31, 18),
                    #  'clear': None,
                    #  'punches': [(141, datetime.datetime(2021, 5, 18, 16, 31, 25)),
                    #              (143, datetime.datetime(2021, 5, 18, 16, 31, 31)),
                    #              (145, datetime.datetime(2021, 5, 18, 16, 31, 38)),
                    #              (143, datetime.datetime(2021, 5, 18, 16, 31, 44)),
                    #             ],
                    # }
                    #
                    card_data = si.read_sicard()

                    item = self.convert(card_type=card_type, card_data=card_data)
                    self.protocol(item=item)
                    print("")
                    print("Entry time:  ", item["entryTime"])
                    print("Card number: ", item["controlCard"])
                    print("Start time:  ", item.get("startTime", None))
                    print("Finish time: ", item.get("finishTime", None))
                    print("Controls:    ", len(item.get("punches", 0)))

                    r = self.webSocketClient.send_and_receive(item=item)

                    if "status" in r:
                        print(r["status"])
                        # beep
                        si.ack_sicard()
                except sireader.SIReaderCardChanged:
                    self.webSocketClient.set_state(
                        entry_type="cardRemoved",
                        entry_time=datetime.datetime.now(),
                    )

        finally:
            try:
                if not extended_protocol:
                    # change back to basic protocl
                    si.set_extended_protocol(False)
            finally:
                si.disconnect()
                # send readerDisconnected message
                # send readerDisconnected message
                r = self.webSocketClient.set_state(
                    entry_type="readerDisconnected",
                    entry_time=datetime.datetime.now(),
                )

    def process_cards(self) -> None:
        print("#### process cards ###")
        while True:
            try:
                self.reader()
            except (sireader.SIReaderException, sireader.SIReaderTimeout, OSError) as e:
                print(f"SIReader or OSError exception:\n{str(e)}")
                time.sleep(5)

    def process_log(self, cardreader_log: pathlib.Path) -> None:
        send_all_entries = False
        with open(cardreader_log, "r") as f:
            r = self.webSocketClient.set_state(
                entry_type="readerConnected",
                entry_time=datetime.datetime.now(),
            )

            line = f.readline()
            while line != "":
                if not send_all_entries:
                    inp = input("Weiter? ")
                else:
                    inp = ""

                if inp == "q":
                    break
                elif inp == "a":
                    send_all_entries = True
                elif inp == "c":
                    self.webSocketClient.set_state(
                        entry_type="readerConnected",
                        entry_time=datetime.datetime.now(),
                    )
                elif inp == "d":
                    self.webSocketClient.set_state(
                        entry_type="readerDisconnected",
                        entry_time=datetime.datetime.now(),
                    )
                elif inp == "i":
                    self.webSocketClient.set_state(
                        entry_type="cardInserted",
                        entry_time=datetime.datetime.now(),
                        card=json.loads(line)["controlCard"],
                    )
                elif inp == "r":
                    self.webSocketClient.set_state(
                        entry_type="cardRemoved",
                        entry_time=datetime.datetime.now(),
                    )
                else:
                    item = json.loads(line)
                    line = f.readline()

                    jsonschema.validate(item, self.schema_cardreader_log)
                    print(f"{str(item.get('controlCard', item['entryType']))} ...")

                    r = self.webSocketClient.send_and_receive(item=item)
                    print(r)


def main() -> Optional[int]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".ooresults" / "config.ini",
    )
    parser.add_argument("-f", "--file", type=pathlib.Path)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    config_file = pathlib.Path(args.config)
    if not config_file.exists():
        parser.error(f"File {str(config_file)} not found")

    config = configparser.ConfigParser()
    config.read(config_file)

    # check config file
    #
    #  [Cardreader]
    #  host = localhost
    #  ssl_cert = cert/cert.pem
    #  ssl_verify = true
    #  key = 4711
    #  serial_number =
    #
    try:
        if not config.has_section("Cardreader"):
            raise RuntimeError("Section [Cardreader] missing")
        if not config.has_option("Cardreader", "host"):
            raise RuntimeError("Section [Cardreader]: option 'host' missing")
        if not config.has_option("Cardreader", "key"):
            raise RuntimeError("Section [Cardreader]: option 'key' missing")
    except RuntimeError as e:
        print(f"Error in file {str(config_file)}:")
        print(f"  {str(e)}")
        return 2

    try:
        host = config["Cardreader"]["host"]
        key = config["Cardreader"]["key"]
        ssl_cert = config.get("Cardreader", "ssl_cert", fallback=None)
        serial_number = config.get("Cardreader", "serial_number", fallback=None)
        try:
            ssl_verify = config.getboolean("Cardreader", "ssl_verify", fallback=True)
        except ValueError:
            parser.error(
                "Allowed values for 'ssl_verify' are 'true', 'false', 'on', 'off', 'yes', 'no'"
            )

        # check ssl options
        if ssl_cert and not pathlib.Path(ssl_cert).exists():
            parser.error(f'Certificate file "{ssl_cert}" not found')

        print(f"Host:   {str(host)}")
        print(f"Cert:   {str(ssl_cert)}")
        print(f"Verify: {str(ssl_verify)}")
        print(f"Key:    {str(key)}")
        print(f"Serial: {str(serial_number)}")
        print("")

        # websocket.enableTrace(True)
        webSocketClient = WebSocketClient(
            host=host, key=key, ssl_cert=ssl_cert, ssl_verify=ssl_verify
        )
        webSocketClient.start()

        cardreader = Cardreader(
            webSocketClient=webSocketClient, serial_number=serial_number
        )
        if args.file is None:
            cardreader.process_cards()
        else:
            cardreader.process_log(cardreader_log=args.file)

    except KeyboardInterrupt:
        pass

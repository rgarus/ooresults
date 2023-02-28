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


import sys
import time

import sireader
import serial.tools.list_ports


def connect() -> sireader.SIReaderReadout:
    errors = ""
    for port in serial.tools.list_ports.grep("sportident"):
        try:
            si = sireader.SIReaderReadout(port.device)
            return si
        except (sireader.SIReaderException, sireader.SIReaderTimeout) as msg:
            errors += f"port: {port.device}: {msg}\n"
            pass
    else:
        errors = "No SI Reader found" if errors == "" else errors
    raise sireader.SIReaderException(f"No SI Reader found. Possible reasons: {errors}")


def main():
    while True:
        try:
            try:
                # connect to base station, the station is automatically detected,
                # if this does not work, give the path to the port as an argument
                # see the pyserial documentation for further information.
                si = connect()

                # set to basic protocol mode
                si.poll_sicard()
                print("Setting legacy mode ...")
                si.set_extended_protocol(False)
                print("Legacy mode set")
                break
            except (sireader.SIReaderException, sireader.SIReaderTimeout, OSError) as e:
                print(f"SIReader or OSError exception:\n{str(e)}")
                time.sleep(2)

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    sys.exit(main())

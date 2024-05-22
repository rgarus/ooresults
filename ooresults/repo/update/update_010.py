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


import io
import logging
import pickle
import sqlite3
import sys

from ooresults.repo.result_type import SpStatus


VERSION = 10


class UnpicklerZoneInfo(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if name == "ZoneInfo":
            if sys.version_info.major >= 3 and sys.version_info.minor >= 9:
                if module == "backports.zoneinfo":
                    module = "zoneinfo"
            else:
                if module == "zoneinfo":
                    module = "backports.zoneinfo"

        return pickle.Unpickler.find_class(self, module, name)


def update(path: str = "ooresults.sqlite"):
    conn = sqlite3.connect(database=path)
    try:
        c = conn.cursor()

        # modify SplitTime status (str -> SpStatus)
        c.execute("SELECT * FROM entries")
        data = list(c.fetchall())

        # 0  'id INTEGER PRIMARY KEY'
        # 1  'event_id INTEGER NOT NULL'
        # 2  'competitor_id INTEGER'
        # 3  'class_id INTEGER'
        # 4  'club_id INTEGER'
        # 5  'not_competing BOOL NOT NULL'
        # 6  'result BLOB NOT NULL'
        # 7  'start BLOB NOT NULL'
        # 8  'chip TEXT'
        # 9  'fields BLOB NOT NULL'

        for i in data:
            result = UnpicklerZoneInfo(io.BytesIO(i[6])).load()
            result.__dict__["si_punched_start_time"] = result.punched_start_time
            result.__dict__["si_punched_finish_time"] = result.punched_finish_time
            for split_time in result.split_times:
                split_time.__dict__["si_punch_time"] = split_time.punch_time
            sql = "UPDATE entries SET result = ? WHERE id = ?"
            c.execute(sql, [pickle.dumps(result), i[0]])

        # version
        sql = "UPDATE version SET value = ?"
        c.execute(sql, [VERSION])
        conn.commit()

        # compress database
        c.execute("VACUUM")
        conn.commit()

    except:
        logging.exception("Exception")
        conn.rollback()
        raise
    finally:
        conn.close()

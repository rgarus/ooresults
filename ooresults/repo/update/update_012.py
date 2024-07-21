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
import logging
import pickle
import sqlite3
import io
import sys

from ooresults.repo.class_params import VoidedLeg


VERSION = 12


class UnpicklerMapModules(pickle.Unpickler):
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

        # classes
        c.execute("SELECT params, id FROM classes")
        for params, id in list(c.fetchall()):
            sql = "UPDATE classes SET params = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(params)).load()
            voided_legs = []
            for voided_leg in x.voided_legs:
                voided_legs.append(
                    VoidedLeg(
                        control_1=voided_leg[0],
                        control_2=voided_leg[1],
                    ),
                )
                x.voided_legs = voided_legs
            c.execute(sql, (x.to_json(), id))

        # courses
        c.execute("SELECT controls, id FROM courses")
        for controls, id in list(c.fetchall()):
            sql = "UPDATE courses SET controls = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(controls)).load()
            c.execute(sql, (json.dumps(x), id))

        # events
        c.execute("SELECT fields, id FROM events")
        for fields, id in list(c.fetchall()):
            sql = "UPDATE events SET fields = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(fields)).load()
            c.execute(sql, (json.dumps(x), id))

        # entries
        c.execute("SELECT result, start, fields, id FROM entries")
        for result, start, fields, id in list(c.fetchall()):
            sql = "UPDATE entries SET result = ?, start = ?, fields = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(result)).load()
            y = UnpicklerMapModules(io.BytesIO(start)).load()
            z = UnpicklerMapModules(io.BytesIO(fields)).load()
            c.execute(sql, (x.to_json(), y.to_json(), json.dumps(z), id))

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

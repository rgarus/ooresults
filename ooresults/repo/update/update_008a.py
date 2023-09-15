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


import logging
import sqlite3


def update(path: str = "ooresults.sqlite"):
    conn = sqlite3.connect(database=path)
    try:
        c = conn.cursor()

        # delete club with empty name, use None instead
        c.execute('SELECT id FROM clubs WHERE name = ""')
        for id in list(c.fetchall()):
            sql = "UPDATE competitors SET club_id = NULL WHERE club_id = ?"
            c.execute(sql, id)
            sql = "UPDATE entries SET club_id = NULL WHERE club_id = ?"
            c.execute(sql, id)
            sql = "DELETE FROM clubs WHERE id = ?"
            c.execute(sql, id)

        conn.commit()
    except:
        logging.exception("Exception")
        conn.rollback()
        raise
    finally:
        conn.close()

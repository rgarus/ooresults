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

from ooresults.repo.update import update_013


VERSION = 13


def update_tables(db: sqlite3.Connection) -> None:
    db.execute("BEGIN EXCLUSIVE TRANSACTION")

    cur = db.execute("SELECT value FROM version")
    c = cur.fetchone()
    if not c:
        raise RuntimeError("DB error - table version is empty")

    else:
        version = c["value"]
        logging.info(f"DB version is {version}")

        if version > VERSION:
            raise RuntimeError(
                f"DB version to high - version = {version}, but must be at most {VERSION}"
            )

        elif version < VERSION:
            db.rollback()

            if version <= 11:
                raise RuntimeError(
                    f"DB version to low - version = {version}, but must be at least 12"
                )
            if version <= 12:
                logging.info("Update DB to version 13 ...")
                update_013.update(db=db)

            logging.info(f"DB updated to version {VERSION}")
        else:
            db.rollback()

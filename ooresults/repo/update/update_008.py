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
import pickle
import sqlite3
import io
import sys


VERSION = 8


old_module_names = [
    "o_results.handler.classes",
    "o_results.handler.clubs",
    "o_results.handler.competitors",
    "o_results.handler.courses",
    "o_results.handler.demo_reader",
    "o_results.handler.entries",
    "o_results.handler.events",
    "o_results.handler.handicap",
    "o_results.handler.model",
    "o_results.handler.results",
    "o_results.handler.series",
    "o_results.handler.webapi.result",
    "o_results.pdf.pdf",
    "o_results.pdf.result",
    "o_results.pdf.series",
    "o_results.pdf.splittimes",
    "o_results.pdf.team_result",
    "o_results.plugins.imports.competitors.oc_muenchen_database",
    "o_results.plugins.imports.entries.oo_net_text_csv",
    "o_results.plugins.imports.entries.oo_net_web",
    "o_results.plugins.imports.entries.text",
    "o_results.plugins.iof_class_list",
    "o_results.plugins.iof_competitor_list",
    "o_results.plugins.iof_course_data",
    "o_results.plugins.iof_entry_list",
    "o_results.plugins.iof_result_list",
    "o_results.plugins.oe2003",
    "o_results.repo.class_params",
    "o_results.repo.mem_repo",
    "o_results.repo.repo",
    "o_results.repo.result_type",
    "o_results.repo.series_type",
    "o_results.repo.sqlite_repo",
    "o_results.repo.start_type",
    "o_results.utils.globals",
    "o_results.websocket_server.si",
    "o_results.websocket_server.websocket_handler",
    "o_results.websocket_server.websocket_server",
]


class UnpicklerMapModules(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if module in old_module_names:
            module = module.replace("o_results.", "ooresults.")

        elif name == "ZoneInfo":
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
            c.execute(sql, (pickle.dumps(x), id))

        # courses
        c.execute("SELECT controls, id FROM courses")
        for controls, id in list(c.fetchall()):
            sql = "UPDATE courses SET controls = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(controls)).load()
            c.execute(sql, (pickle.dumps(x), id))

        # events
        c.execute("SELECT fields, id FROM events")
        for fields, id in list(c.fetchall()):
            sql = "UPDATE events SET fields = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(fields)).load()
            c.execute(sql, (pickle.dumps(x), id))

        # entries
        c.execute("SELECT result, start, fields, id FROM entries")
        for result, start, fields, id in list(c.fetchall()):
            sql = "UPDATE entries SET result = ?, start = ?, fields = ? WHERE id = ?"
            x = UnpicklerMapModules(io.BytesIO(result)).load()
            y = UnpicklerMapModules(io.BytesIO(start)).load()
            z = UnpicklerMapModules(io.BytesIO(fields)).load()
            c.execute(sql, (pickle.dumps(x), pickle.dumps(y), pickle.dumps(z), id))

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

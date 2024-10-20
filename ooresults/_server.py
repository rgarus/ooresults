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
import argparse
import re
import base64
import pathlib
import sys
import sqlite3
from typing import Optional

import web
from cheroot.server import HTTPServer
from cheroot.ssl.builtin import BuiltinSSLAdapter

from ooresults import configuration
from ooresults.model import model
from ooresults.handler import results
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.user import Users
from ooresults.utils import rental_cards
from ooresults.utils.globals import t_globals
from ooresults.websocket_server.websocket_server import WebSocketServer


web.config.debug = False


### Templates
templates = pathlib.Path(__file__).resolve().parent / "templates"
render_base = web.template.render(templates, base="base", globals={"str": str})
render = web.template.render(templates, globals=t_globals)


class Root:
    def GET(self):
        events = model.get_events()
        for event in events:
            if event.publish:
                event, class_results = model.event_class_results(event_id=event.id)
                columns = results.build_columns(class_results)
                results_table = render.results_table(event, class_results, columns)
                return render.root(results_table)
        else:
            return render.root(None)


class Login:
    def GET(self):
        try:
            Users.update()
        except Exception as e:
            return str(e)
        raise web.seeother("/")


class Admin:
    def GET(self):
        events_table = render.events_table(model.get_events())
        events_tab_content = render.events_tab_content(events_table)
        entries_table = render.entries_table(None, [])
        entries_tab_content = render.entries_tab_content(entries_table)
        classes_table = render.classes_table(None, [])
        classes_tab_content = render.classes_tab_content(classes_table)
        courses_table = render.courses_table(None, [])
        courses_tab_content = render.courses_tab_content(courses_table)
        results_table = render.results_table(None, [], set())
        results_tab_content = render.results_tab_content(results_table)
        series_table = render.series_table([], [])
        series_tab_content = render.series_tab_content(series_table)
        competitors_table = render.competitors_table([])
        competitors_tab_content = render.competitors_tab_content(competitors_table)
        clubs_table = render.clubs_table([])
        clubs_tab_content = render.clubs_tab_content(clubs_table)
        return render_base.main(
            events_tab_content,
            entries_tab_content,
            classes_tab_content,
            courses_tab_content,
            results_tab_content,
            series_tab_content,
            competitors_tab_content,
            clubs_tab_content,
        )


class Static:
    def GET(self, filename):
        """searches for and returns a requested static file or 404s out"""
        try:
            file = pathlib.Path(__file__).parent / "static" / filename
            with open(file, "r") as f:
                return f.read()
        except FileNotFoundError:
            raise web.notfound()  # file not found


def my_processor(handler):
    if web.ctx.env.get("PATH_INFO") not in (
        "/",
        "/favicon.ico",
    ) and not web.ctx.env.get("PATH_INFO").startswith("/mystatic/"):
        auth = web.ctx.env.get("HTTP_AUTHORIZATION")
        if auth is not None:
            auth = re.sub("^Basic ", "", auth)
            auth = base64.b64decode(auth.encode("ascii")).decode("utf8")
            username, password = auth.split(":")
            if not Users.check(username=username, password=password):
                web.header("WWW-Authenticate", 'Basic realm="Authentication required"')
                web.ctx.status = "401 Unauthorized"
                return render.unauthorized()
        else:
            web.header("WWW-Authenticate", 'Basic realm="Authentication required"')
            web.ctx.status = "401 Unauthorized"
            return render.unauthorized()

    result = handler()
    return result


def main() -> Optional[int]:
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        filename="ooresults_server.log",
        level=logging.INFO,
    )
    logging.info("-------- ooresults.server --------")

    ### Url mappings
    urls = (
        "/",
        "Root",
        "/admin",
        "Admin",
        "/login",
        "Login",
        "/mystatic/(.*)",
        "Static",
        "/event/update",
        "ooresults.handler.events.Update",
        "/event/add",
        "ooresults.handler.events.Add",
        "/event/fill_edit_form",
        "ooresults.handler.events.FillEditForm",
        "/event/delete",
        "ooresults.handler.events.Delete",
        "/entry/update",
        "ooresults.handler.entries.Update",
        "/entry/import",
        "ooresults.handler.entries.Import",
        "/entry/export",
        "ooresults.handler.entries.Export",
        "/entry/add",
        "ooresults.handler.entries.Add",
        "/entry/fill_edit_form",
        "ooresults.handler.entries.FillEditForm",
        "/entry/fill_competitors_form",
        "ooresults.handler.entries.FillCompetitorsForm",
        "/entry/fill_result_form",
        "ooresults.handler.entries.FillResultForm",
        "/entry/delete",
        "ooresults.handler.entries.Delete",
        "/entry/splitTimes",
        "ooresults.handler.entries.SplitTimes",
        "/entry/editPunch",
        "ooresults.handler.entries.EditPunch",
        "/result/update",
        "ooresults.handler.results.Update",
        "/result/pdfResult",
        "ooresults.handler.results.PdfResult",
        "/result/pdfSplittimes",
        "ooresults.handler.results.PdfSplittimes",
        "/result/pdfTeamResult",
        "ooresults.handler.results.PdfTeamResult",
        "/class/update",
        "ooresults.handler.classes.Update",
        "/class/import",
        "ooresults.handler.classes.Import",
        "/class/export",
        "ooresults.handler.classes.Export",
        "/class/add",
        "ooresults.handler.classes.Add",
        "/class/fill_edit_form",
        "ooresults.handler.classes.FillEditForm",
        "/class/delete",
        "ooresults.handler.classes.Delete",
        "/course/update",
        "ooresults.handler.courses.Update",
        "/course/import",
        "ooresults.handler.courses.Import",
        "/course/export",
        "ooresults.handler.courses.Export",
        "/course/add",
        "ooresults.handler.courses.Add",
        "/course/fill_edit_form",
        "ooresults.handler.courses.FillEditForm",
        "/course/delete",
        "ooresults.handler.courses.Delete",
        "/competitor/update",
        "ooresults.handler.competitors.Update",
        "/competitor/import",
        "ooresults.handler.competitors.Import",
        "/competitor/export",
        "ooresults.handler.competitors.Export",
        "/competitor/add",
        "ooresults.handler.competitors.Add",
        "/competitor/fill_edit_form",
        "ooresults.handler.competitors.FillEditForm",
        "/competitor/delete",
        "ooresults.handler.competitors.Delete",
        "/club/update",
        "ooresults.handler.clubs.Update",
        "/club/add",
        "ooresults.handler.clubs.Add",
        "/club/fill_edit_form",
        "ooresults.handler.clubs.FillEditForm",
        "/club/delete",
        "ooresults.handler.clubs.Delete",
        "/series/update",
        "ooresults.handler.series.Update",
        "/series/fill_settings_form",
        "ooresults.handler.series.FillSettingsForm",
        "/series/settings",
        "ooresults.handler.series.Settings",
        "/series/pdfResult",
        "ooresults.handler.series.PdfResult",
        "/series/csvResult",
        "ooresults.handler.series.CsvResult",
        "/si1",
        "ooresults.handler.si.Si1",
        "/si2",
        "ooresults.handler.si.Si2",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=pathlib.Path, dest="main_path")
    parser.add_argument("-d", "--database", type=pathlib.Path, dest="database")
    # web.application().run() use sys.argv to determine
    # the port number of the http server
    # we remove parsed arguments from sys.argv
    args, left = parser.parse_known_args()
    sys.argv = sys.argv[:1] + left

    main_path = args.main_path
    if main_path:
        if not args.main_path.exists():
            parser.error(f"Path {str(args.main_path)} not found")
        if not args.main_path.is_dir():
            parser.error(f"Path {str(args.main_path)} is not a directory")
    else:
        main_path = pathlib.Path.home() / ".ooresults"

    database = args.database
    if database:
        if not args.database.exists():
            parser.error(f"Database {str(args.database)} not found")
    else:
        database = main_path / "ooresults.sqlite"

    try:
        config = configuration.Config(path=main_path)
    except (RuntimeError, FileNotFoundError) as e:
        print(f'Error in file {str(main_path / "config.ini")}:')
        print(f"  {str(e)}")
        return 2

    rental_cards.read_rental_cards(path=main_path / "rental_cards.txt")

    try:
        model.db = SqliteRepo(
            db=str(database),
        )
    except (RuntimeError, sqlite3.Error):
        exc_type, exc_value, _ = sys.exc_info()
        logging.error(f"{exc_type.__module__}.{exc_type.__name__}: {exc_value}")
        print(f"{exc_type.__module__}.{exc_type.__name__}: {exc_value}")
        return 2

    if config.demo_reader:
        urls += ("/demo", "ooresults.handler.demo_reader.Update")

    Users.update(path=main_path / "users.json")

    app = web.application(urls, globals())
    HTTPServer.ssl_adapter = BuiltinSSLAdapter(
        certificate=config.ssl_cert,
        private_key=config.ssl_key,
    )

    try:
        app.add_processor(my_processor)
        try:
            model.websocket_server = WebSocketServer(
                demo_reader=config.demo_reader,
                import_stream=config.import_stream,
                ssl_cert=config.ssl_cert,
                ssl_key=config.ssl_key,
            )
        except:
            model.websocket_server = WebSocketServer(
                demo_reader=config.demo_reader,
                import_stream=config.import_stream,
            )
        model.websocket_server.start()
        logging.info("Webserver started")
        app.run()
    except KeyboardInterrupt:
        logging.info("Webserver stopped")

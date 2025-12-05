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
import base64
import logging
import pathlib
import re
import sqlite3
import sys
import warnings
from typing import Optional

import bottle

import ooresults.handler.classes
import ooresults.handler.clubs
import ooresults.handler.competitors
import ooresults.handler.courses
import ooresults.handler.demo_reader
import ooresults.handler.entries
import ooresults.handler.events
import ooresults.handler.results
import ooresults.handler.root
import ooresults.handler.series
import ooresults.handler.si1
import ooresults.handler.si2
from ooresults import configuration
from ooresults import model
from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.user import Users
from ooresults.utils import render
from ooresults.utils import rental_cards
from ooresults.websocket_server.websocket_server import WebSocketServer


bottle.debug(False)


@bottle.route("/login", method="GET")
def login():
    try:
        Users.update()
    except Exception as e:
        return str(e)
    raise bottle.redirect("/")


@bottle.route("/admin", method="GET")
def admin():
    return render.main(events=model.events.get_events())


@bottle.route("/mystatic/<filepath:path>")
def server_static(filepath):
    return bottle.static_file(filepath, root=pathlib.Path(__file__).parent / "static")


def unauthorized() -> bottle.HTTPResponse:
    return bottle.HTTPResponse(
        status=401,
        headers={"WWW-Authenticate": 'Basic realm="Authentication required"'},
        body=render.unauthorized(),
    )


@bottle.hook("after_request")
def after_request():
    logging.info(
        f"{bottle.request.method}  {bottle.request.remote_addr}  {bottle.request.path}  {bottle.response.status_line}"
    )


def my_plugin(callback):
    def wrapper(*args, **kwargs):
        path = bottle.request.environ["PATH_INFO"]
        if path not in ("/", "/favicon.ico") and not path.startswith("/mystatic/"):
            auth = bottle.request.environ.get("HTTP_AUTHORIZATION", None)
            if auth is not None:
                auth = re.sub("^Basic ", "", auth)
                auth = base64.b64decode(auth.encode("ascii")).decode("utf8")
                username, password = auth.split(":")
                if not Users.check(username=username, password=password):
                    return unauthorized()
            else:
                return unauthorized()
        try:
            return callback(*args, **kwargs)
        except bottle.MultipartError as e:
            logging.error(f"Exception: {type(e)}, {e}")
            return bottle.HTTPResponse(status=413, body="Content too large")
        except Exception:
            logging.exception("Internal server error")
            return bottle.HTTPResponse(status=500, body="Internal server error")
        finally:
            model.db.close()

    return wrapper


def main() -> Optional[int]:
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        filename="ooresults_server.log",
        level=logging.INFO,
    )
    logging.info("-------- ooresults.server --------")
    logging.info(f"{sys.version}, {sys.platform}")
    logging.info(f"{sys.executable}")

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=pathlib.Path, dest="main_path")
    parser.add_argument("-d", "--database", type=pathlib.Path, dest="database")
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
        model.db = SqliteRepo(db=str(database))
    except (RuntimeError, sqlite3.Error):
        exc_type, exc_value, _ = sys.exc_info()
        logging.error(f"{exc_type.__module__}.{exc_type.__name__}: {exc_value}")
        print(f"{exc_type.__module__}.{exc_type.__name__}: {exc_value}")
        return 2

    if config.demo_reader:
        bottle.route("/demo")(ooresults.handler.demo_reader.get_update)

    Users.update(path=main_path / "users.json")

    try:
        model.results.websocket_server = WebSocketServer(
            demo_reader=config.demo_reader,
            import_stream=config.import_stream,
            ssl_cert=config.ssl_cert,
            ssl_key=config.ssl_key,
        )
    except Exception:
        model.results.websocket_server = WebSocketServer(
            demo_reader=config.demo_reader,
            import_stream=config.import_stream,
        )
    model.results.websocket_server.start()
    logging.info("WebSocketServer started")

    bottle.install(my_plugin)
    bottle.run(
        server="cheroot",
        host="0.0.0.0",
        port=8080,
        debug=True,
        certfile=config.ssl_cert,
        keyfile=config.ssl_key,
    )
    model.results.websocket_server.close()
    logging.info("WebSockerServer stopped")

    # Suppress ResourceWarning message:
    # ResourceWarning: unclosed database in <sqlite3.Connection object at ...>
    warnings.filterwarnings("ignore", category=ResourceWarning)

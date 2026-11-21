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


import pathlib
import sqlite3
from collections.abc import Iterator

import pytest

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.repo.update.update_tables import VERSION
from ooresults.repo.update.update_tables import update_tables


@pytest.fixture
def database(tmp_path: pathlib.Path) -> Iterator[sqlite3.Connection]:
    path = tmp_path / "ooresults.sqlite"
    repo = SqliteRepo(db=str(path))
    repo.close()

    db = sqlite3.connect(database=str(path))
    db.row_factory = sqlite3.Row
    yield db
    db.close()


def test_current_version_ends_transaction(database: sqlite3.Connection) -> None:
    update_tables(db=database)
    assert not database.in_transaction


def test_version_too_low_raises_and_ends_transaction(
    database: sqlite3.Connection,
) -> None:
    database.execute("UPDATE version SET value = 1")
    database.commit()

    with pytest.raises(RuntimeError, match="DB version too low - version = "):
        update_tables(db=database)
    assert not database.in_transaction


def test_version_too_high_raises_and_ends_transaction(
    database: sqlite3.Connection,
) -> None:
    database.execute("UPDATE version SET value = ?", (VERSION + 1,))
    database.commit()

    with pytest.raises(RuntimeError, match="DB version too high - version = "):
        update_tables(db=database)
    assert not database.in_transaction


def test_empty_version_table_raises_and_ends_transaction(
    database: sqlite3.Connection,
) -> None:
    database.execute("DELETE FROM version")
    database.commit()

    with pytest.raises(RuntimeError, match="DB error - table 'version' is empty"):
        update_tables(db=database)
    assert not database.in_transaction

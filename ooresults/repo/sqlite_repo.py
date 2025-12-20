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


import copy
import datetime
import json
import logging
import sqlite3
import threading
from typing import Optional

from ooresults.otypes import result_type
from ooresults.otypes import series_type
from ooresults.otypes import start_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import ClassUsedError
from ooresults.repo.repo import ClubUsedError
from ooresults.repo.repo import CompetitorUsedError
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import CourseUsedError
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import OperationalError
from ooresults.repo.repo import Repo
from ooresults.repo.repo import TransactionMode
from ooresults.repo.update import update_tables


class SqliteRepo(Repo):
    def __init__(self, db: str = "ooresults.sqlite") -> None:
        self.database = db
        self._ctx = threading.local()

        # sqlite3.register_adapter(bool, int)
        # sqlite3.register_converter("BOOLEAN", lambda v: v != '0')

        cur = self.db.execute(
            "SELECT name FROM sqlite_schema WHERE type='table' AND name='version'",
        )
        c = cur.fetchone()

        if not c:
            # create and initialize database tables
            with self.transaction(mode=TransactionMode.EXCLUSIVE):
                cur = self.db.cursor()
                try:
                    cur.execute(
                        """
                        CREATE TABLE version (
                            value INTEGER PRIMARY KEY
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE clubs (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE competitors (
                            id INTEGER PRIMARY KEY,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            club_id INTEGER REFERENCES clubs(id),
                            gender TEXT,
                            year INTEGER,
                            chip TEXT,
                            UNIQUE (first_name, last_name)
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE events (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            date TEXT,
                            key TEXT UNIQUE,
                            publish BOOL NOT NULL,
                            series TEXT,
                            fields BLOB NOT NULL,
                            streaming_address TEXT,
                            streaming_key TEXT,
                            streaming_enabled BOOL
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE courses (
                            id INTEGER PRIMARY KEY,
                            event_id INTEGER NOT NULL REFERENCES events(id),
                            name TEXT NOT NULL,
                            length FLOAT,
                            climb FLOAT,
                            controls BLOB NOT NULL,
                            UNIQUE (event_id, name)
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE classes (
                            id INTEGER PRIMARY KEY,
                            event_id INTEGER NOT NULL REFERENCES events(id),
                            name TEXT NOT NULL,
                            short_name TEXT,
                            course_id INTEGER REFERENCES courses(id),
                            params BLOB NOT NULL,
                            UNIQUE (event_id, name)
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE entries (
                            id INTEGER PRIMARY KEY,
                            event_id INTEGER NOT NULL REFERENCES events(id),
                            competitor_id INTEGER REFERENCES competitors(id),
                            class_id INTEGER REFERENCES classes(id),
                            club_id INTEGER REFERENCES clubs(id),
                            not_competing BOOL NOT NULL,
                            result BLOB NOT NULL,
                            start BLOB NOT NULL,
                            chip TEXT,
                            fields BLOB NOT NULL
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE INDEX entries_idx1 ON entries(
                            event_id,
                            competitor_id
                        )""",
                    )
                    cur.execute(
                        """
                        CREATE TABLE settings (
                            name TEXT NOT NULL,
                            nr_of_best_results INTEGER,
                            mode TEXT NOT NULL,
                            maximum_points INTEGER NOT NULL,
                            decimal_places INTEGER NOT NULL
                        )""",
                    )

                    cur.execute(
                        "INSERT INTO version VALUES(?)",
                        (update_tables.VERSION,),
                    )
                    logging.info(f"DB version initialized to {update_tables.VERSION}")
                except:
                    logging.exception(
                        f"Error during DB initialization to version {update_tables.VERSION}"
                    )
                    raise
                finally:
                    cur.close()
        else:
            update_tables.update_tables(db=self.db)

    @property
    def db(self) -> sqlite3.Connection:
        if not hasattr(self._ctx, "db"):
            self._ctx.db = sqlite3.connect(database=self.database)
            self._ctx.db.row_factory = sqlite3.Row
            self._ctx.db.execute("PRAGMA foreign_keys = on")

        return self._ctx.db

    def start_transaction(self, mode: TransactionMode = TransactionMode.DEFERRED):
        try:
            self.db.execute(f"BEGIN {mode.value} TRANSACTION")
        except sqlite3.OperationalError as e:
            raise OperationalError(str(e))

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def close(self):
        if hasattr(self._ctx, "db"):
            self.db.rollback()
            self.db.close()
            del self._ctx.db

    def get_classes(self, event_id: int) -> list[ClassInfoType]:
        cur = self.db.execute(
            """
            SELECT
                classes.id,
                classes.name,
                classes.short_name,
                courses.id AS course_id,
                courses.name AS course_name,
                courses.length AS course_length,
                courses.climb AS course_climb,
                courses.controls,
                classes.params
            FROM classes
            LEFT JOIN courses ON classes.course_id=courses.id
            WHERE classes.event_id=?
            ORDER BY classes.name ASC""",
            (event_id,),
        )

        classes = []
        for c in cur:
            number_of_controls = None
            if c["controls"] is not None:
                controls = json.loads(c["controls"])
                number_of_controls = len(controls)
            classes.append(
                ClassInfoType(
                    id=c["id"],
                    name=c["name"],
                    short_name=c["short_name"],
                    course_id=c["course_id"],
                    course_name=c["course_name"],
                    course_length=c["course_length"],
                    course_climb=c["course_climb"],
                    number_of_controls=number_of_controls,
                    params=ClassParams.from_json(json_data=c["params"]),
                )
            )
        return classes

    def get_class(self, id: int) -> ClassType:
        cur = self.db.execute(
            """
            SELECT
                id,
                event_id,
                name,
                short_name,
                course_id,
                params
            FROM classes WHERE id=?""",
            (id,),
        )
        c = cur.fetchone()
        if c:
            return ClassType(
                id=c["id"],
                event_id=c["event_id"],
                name=c["name"],
                short_name=c["short_name"],
                course_id=c["course_id"],
                params=ClassParams.from_json(json_data=c["params"]),
            )
        else:
            raise KeyError

    def add_class(
        self,
        event_id: int,
        name: str,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        try:
            cur = self.db.execute(
                """
                INSERT into classes (
                    event_id,
                    name,
                    short_name,
                    course_id,
                    params
                )
                VALUES(?, ?, ?, ?, ?)""",
                (
                    event_id,
                    name,
                    short_name,
                    course_id,
                    params.to_json(),
                ),
            )
            return cur.lastrowid

        except sqlite3.IntegrityError:
            raise ConstraintError("Class already exist")

    def update_class(
        self,
        id: int,
        name: str,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ):
        try:
            cur = self.db.execute(
                """
                UPDATE classes SET
                    name=?,
                    short_name=?,
                    course_id=?,
                    params=?
                WHERE id=?""",
                (
                    name,
                    short_name,
                    course_id,
                    params.to_json(),
                    id,
                ),
            )
            if cur.rowcount == 0:
                raise KeyError

        except sqlite3.IntegrityError:
            raise ConstraintError("Class already exist")

    def delete_classes(self, event_id: int):
        cur = self.db.execute(
            "SELECT id FROM entries WHERE event_id=?",
            (event_id,),
        )
        if cur.fetchone():
            raise ClassUsedError
        else:
            self.db.execute(
                "DELETE FROM classes WHERE event_id=?",
                (event_id,),
            )

    def delete_class(self, id: int):
        cur = self.db.execute(
            "SELECT id FROM entries WHERE class_id=?",
            (id,),
        )
        if cur.fetchone():
            raise ClassUsedError
        else:
            self.db.execute(
                "DELETE FROM classes WHERE id=?",
                (id,),
            )

    def get_courses(self, event_id: int) -> list[CourseType]:
        cur = self.db.execute(
            """
            SELECT
                id,
                event_id,
                name,
                length,
                climb,
                controls
            FROM courses
            WHERE event_id=?
            ORDER BY name ASC""",
            (event_id,),
        )

        courses = []
        for c in cur:
            courses.append(
                CourseType(
                    id=c["id"],
                    event_id=c["event_id"],
                    name=c["name"],
                    length=c["length"],
                    climb=c["climb"],
                    controls=json.loads(c["controls"]),
                )
            )
        return courses

    def get_course(self, id: int) -> CourseType:
        cur = self.db.execute(
            """
            SELECT
                id,
                event_id,
                name,
                length,
                climb,
                controls
            FROM courses WHERE id=?""",
            (id,),
        )
        c = cur.fetchone()
        if c:
            return CourseType(
                id=c["id"],
                event_id=c["event_id"],
                name=c["name"],
                length=c["length"],
                climb=c["climb"],
                controls=json.loads(c["controls"]),
            )
        else:
            raise KeyError

    def add_course(
        self,
        event_id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: list[str],
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        try:
            cur = self.db.execute(
                """
                INSERT into courses (
                    event_id,
                    name,
                    length,
                    climb,
                    controls
                )
                VALUES(?, ?, ?, ?, ?)""",
                (
                    event_id,
                    name,
                    length,
                    climb,
                    json.dumps(controls),
                ),
            )
            return cur.lastrowid

        except sqlite3.IntegrityError:
            raise ConstraintError("Course already exist")

    def update_course(
        self,
        id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: list[str],
    ):
        try:
            cur = self.db.execute(
                """
                UPDATE courses SET
                    name=?,
                    length=?,
                    climb=?,
                    controls=?
                WHERE id=?""",
                (
                    name,
                    length,
                    climb,
                    json.dumps(controls),
                    id,
                ),
            )
            if cur.rowcount == 0:
                raise KeyError

        except sqlite3.IntegrityError:
            raise ConstraintError("Course already exist")

    def delete_courses(self, event_id: int):
        cur = self.db.execute(
            "SELECT id FROM classes WHERE event_id=? and course_id is not null",
            (event_id,),
        )
        if cur.fetchone():
            raise CourseUsedError
        else:
            self.db.execute(
                "DELETE FROM courses WHERE event_id=?",
                (event_id,),
            )

    def delete_course(self, id: int):
        cur = self.db.execute(
            "SELECT id FROM classes WHERE course_id=?",
            (id,),
        )
        if cur.fetchone():
            raise CourseUsedError
        else:
            self.db.execute(
                "DELETE FROM courses WHERE id=?",
                (id,),
            )

    def get_clubs(self) -> list[ClubType]:
        cur = self.db.execute(
            "SELECT id, name FROM clubs ORDER BY name ASC",
            (),
        )
        clubs = []
        for c in cur:
            clubs.append(
                ClubType(
                    id=c["id"],
                    name=c["name"],
                )
            )
        return clubs

    def get_club(self, id: int) -> ClubType:
        cur = self.db.execute(
            "SELECT id, name FROM clubs WHERE id=?",
            (id,),
        )
        c = cur.fetchone()
        if c:
            return ClubType(
                id=c["id"],
                name=c["name"],
            )
        else:
            raise KeyError

    def add_club(self, name: str) -> int:
        try:
            cur = self.db.execute(
                "INSERT into clubs (name) VALUES(?)",
                (name,),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ConstraintError("Club already exist")

    def update_club(self, id: int, name: str) -> None:
        try:
            cur = self.db.execute(
                "UPDATE clubs SET name=? WHERE id=?",
                (name, id),
            )
            if cur.rowcount == 0:
                raise KeyError

        except sqlite3.IntegrityError:
            raise ConstraintError("Club already exist")

    def delete_club(self, id: int) -> None:
        cur1 = self.db.execute(
            "SELECT id FROM competitors WHERE club_id=?",
            (id,),
        )
        cur2 = self.db.execute(
            "SELECT id FROM entries WHERE club_id=?",
            (id,),
        )
        if cur1.fetchone() or cur2.fetchone():
            raise ClubUsedError
        else:
            self.db.execute(
                "DELETE FROM clubs WHERE id=?",
                (id,),
            )

    def get_competitors(self) -> list[CompetitorType]:
        cur = self.db.execute(
            """
            SELECT
                competitors.id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                competitors.chip,
                clubs.id AS club_id,
                clubs.name AS club_name
            FROM competitors
            LEFT JOIN clubs ON competitors.club_id = clubs.id
            ORDER BY competitors.last_name ASC, competitors.first_name ASC""",
        )

        competitors = []
        for c in cur:
            competitors.append(
                CompetitorType(
                    id=c["id"],
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                    gender=c["gender"],
                    year=c["year"],
                    chip=c["chip"],
                    club_id=c["club_id"],
                    club_name=c["club_name"],
                )
            )
        return competitors

    def get_competitor(self, id) -> CompetitorType:
        cur = self.db.execute(
            """
            SELECT
                competitors.id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                competitors.chip,
                clubs.id AS club_id,
                clubs.name AS club_name
            FROM competitors
            LEFT JOIN clubs ON competitors.club_id=clubs.id
            WHERE competitors.id=?""",
            (id,),
        )
        c = cur.fetchone()
        if c:
            return CompetitorType(
                id=c["id"],
                first_name=c["first_name"],
                last_name=c["last_name"],
                gender=c["gender"],
                year=c["year"],
                chip=c["chip"],
                club_id=c["club_id"],
                club_name=c["club_name"],
            )
        else:
            raise KeyError

    def get_competitor_by_name(self, first_name: str, last_name: str) -> CompetitorType:
        cur = self.db.execute(
            """
            SELECT
                competitors.id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                competitors.chip,
                clubs.id AS club_id,
                clubs.name AS club_name
            FROM competitors
            LEFT JOIN clubs ON competitors.club_id=clubs.id
            WHERE competitors.first_name=? AND competitors.last_name=?""",
            (
                first_name,
                last_name,
            ),
        )

        c = cur.fetchone()
        if c:
            return CompetitorType(
                id=c["id"],
                first_name=c["first_name"],
                last_name=c["last_name"],
                gender=c["gender"],
                year=c["year"],
                chip=c["chip"],
                club_id=c["club_id"],
                club_name=c["club_name"],
            )
        else:
            raise KeyError

    def add_competitor(
        self,
        first_name: str,
        last_name: str,
        club_id: Optional[int],
        gender: str,
        year: Optional[int],
        chip: str,
    ) -> int:
        try:
            cur = self.db.execute(
                """
                INSERT into competitors (
                    first_name,
                    last_name,
                    club_id,
                    gender,
                    year,
                    chip
                )
                VALUES(?, ?, ?, ?, ?, ?)""",
                (
                    first_name,
                    last_name,
                    club_id,
                    gender,
                    year,
                    chip,
                ),
            )
            return cur.lastrowid

        except sqlite3.IntegrityError:
            raise ConstraintError("Competitor already exist")

    def update_competitor(
        self,
        id: int,
        first_name: str,
        last_name: str,
        club_id: Optional[int],
        gender: str,
        year: Optional[int],
        chip: str,
    ) -> None:
        try:
            cur = self.db.execute(
                """
                UPDATE competitors SET
                    first_name=?,
                    last_name=?,
                    club_id=?,
                    gender=?,
                    year=?,
                    chip=?
                WHERE id=?""",
                (
                    first_name,
                    last_name,
                    club_id,
                    gender,
                    year,
                    chip,
                    id,
                ),
            )
            if cur.rowcount == 0:
                raise KeyError

        except sqlite3.IntegrityError:
            raise ConstraintError("Competitor already exist")

    def delete_competitor(self, id: int) -> None:
        cur = self.db.execute(
            "SELECT id FROM entries WHERE competitor_id=?",
            (id,),
        )
        if cur.fetchone():
            raise CompetitorUsedError
        else:
            self.db.execute(
                "DELETE FROM competitors WHERE id=?",
                (id,),
            )

    def import_competitors(self, competitors: list[dict]) -> None:
        list_of_competitors = []
        for c in competitors:
            club_id = None
            if c["club"]:
                for clb in self.get_clubs():
                    if clb.name == c["club"]:
                        club_id = clb.id
                        break
                else:
                    club_id = self.add_club(name=c["club"])

            try:
                c_name = self.get_competitor_by_name(
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                )
            except KeyError:
                list_of_competitors.append(
                    (
                        c["first_name"],
                        c["last_name"],
                        club_id,
                        c["gender"] if "gender" in c else "",
                        c["year"] if "year" in c else "",
                        c["chip"] if "chip" in c else "",
                    )
                )
            else:
                gender = c_name.gender
                if "gender" in c and c["gender"]:
                    gender = c["gender"]
                year = c_name.year
                if "year" in c and c["year"] is not None:
                    year = c["year"]
                chip = c_name.chip
                if "chip" in c and c["chip"]:
                    chip = c["chip"]
                self.update_competitor(
                    id=c_name.id,
                    first_name=c_name.first_name,
                    last_name=c_name.last_name,
                    club_id=c_name.club_id if club_id is None else club_id,
                    gender=gender,
                    year=year,
                    chip=chip,
                )

        if list_of_competitors:
            self.db.executemany(
                """
                INSERT into competitors (
                    first_name,
                    last_name,
                    club_id,
                    gender,
                    year,
                    chip
                )
                VALUES(?, ?, ?, ?, ?, ?)""",
                list_of_competitors,
            )

    def get_entries(self, event_id: int) -> list[EntryType]:
        cur = self.db.execute(
            """
            SELECT
                entries.id,
                entries.event_id,
                competitors.id AS competitor_id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                entries.class_id,
                classes.name AS class_name,
                entries.not_competing,
                entries.chip,
                entries.fields,
                entries.result,
                entries.start,
                entries.club_id,
                clubs.name AS club_name
            FROM entries
            LEFT JOIN competitors ON entries.competitor_id=competitors.id
            LEFT JOIN classes ON entries.class_id=classes.id
            LEFT JOIN clubs ON entries.club_id=clubs.id
            WHERE entries.event_id=?
            ORDER BY
                competitors.last_name ASC,
                competitors.first_name ASC,
                entries.chip ASC""",
            (event_id,),
        )

        entries = []
        for c in cur:
            fields = {int(key): value for key, value in json.loads(c["fields"]).items()}
            entries.append(
                EntryType(
                    id=c["id"],
                    event_id=c["event_id"],
                    competitor_id=c["competitor_id"],
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                    gender=c["gender"],
                    year=c["year"],
                    class_id=c["class_id"],
                    class_name=c["class_name"],
                    not_competing=bool(c["not_competing"]),
                    chip=c["chip"],
                    fields=fields,
                    result=result_type.PersonRaceResult.from_json(
                        json_data=c["result"]
                    ),
                    start=start_type.PersonRaceStart.from_json(json_data=c["start"]),
                    club_id=c["club_id"],
                    club_name=c["club_name"],
                )
            )
        return entries

    def get_entry(self, id: int) -> EntryType:
        cur = self.db.execute(
            """
            SELECT
                entries.id,
                entries.event_id,
                competitors.id AS competitor_id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                classes.id AS class_id,
                classes.name AS class_name,
                clubs.id AS club_id,
                clubs.name AS club_name,
                entries.not_competing,
                entries.chip,
                entries.fields,
                entries.result,
                entries.start
            FROM entries
            LEFT JOIN competitors ON entries.competitor_id=competitors.id
            LEFT JOIN classes ON entries.class_id=classes.id
            LEFT JOIN clubs ON entries.club_id=clubs.id
            WHERE entries.id=?""",
            (id,),
        )

        c = cur.fetchone()
        if c:
            fields = {int(key): value for key, value in json.loads(c["fields"]).items()}

            return EntryType(
                id=c["id"],
                event_id=c["event_id"],
                competitor_id=c["competitor_id"],
                first_name=c["first_name"],
                last_name=c["last_name"],
                gender=c["gender"],
                year=c["year"],
                class_id=c["class_id"],
                class_name=c["class_name"],
                not_competing=bool(c["not_competing"]),
                chip=c["chip"],
                fields=fields,
                result=result_type.PersonRaceResult.from_json(json_data=c["result"]),
                start=start_type.PersonRaceStart.from_json(json_data=c["start"]),
                club_id=c["club_id"],
                club_name=c["club_name"],
            )
        else:
            raise KeyError

    def get_entry_ids_by_competitor(
        self, event_id: int, competitor_id: int
    ) -> list[int]:
        cur = self.db.execute(
            """
            SELECT id
            FROM entries
            WHERE event_id=? AND competitor_id=?""",
            (
                event_id,
                competitor_id,
            ),
        )
        return [row[0] for row in cur]

    def get_entry_by_name(
        self, event_id: int, first_name: str, last_name: str
    ) -> EntryType:
        cur = self.db.execute(
            """
            SELECT
                entries.id,
                entries.event_id,
                competitors.id AS competitor_id,
                competitors.first_name,
                competitors.last_name,
                competitors.gender,
                competitors.year,
                classes.id AS class_id,
                classes.name AS class_name,
                clubs.id AS club_id,
                clubs.name AS club_name,
                entries.not_competing,
                entries.chip,
                entries.fields,
                entries.result,
                entries.start
            FROM entries
            LEFT JOIN competitors ON entries.competitor_id=competitors.id
            LEFT JOIN classes ON entries.class_id=classes.id
            LEFT JOIN clubs ON entries.club_id=clubs.id
            WHERE entries.event_id=?
                AND competitors.first_name=?
                AND competitors.last_name=?""",
            (
                event_id,
                first_name,
                last_name,
            ),
        )

        c = cur.fetchone()
        if c:
            fields = {int(key): value for key, value in json.loads(c["fields"]).items()}

            return EntryType(
                id=c["id"],
                event_id=c["event_id"],
                competitor_id=c["competitor_id"],
                first_name=c["first_name"],
                last_name=c["last_name"],
                gender=c["gender"],
                year=c["year"],
                class_id=c["class_id"],
                class_name=c["class_name"],
                not_competing=bool(c["not_competing"]),
                chip=c["chip"],
                fields=fields,
                result=result_type.PersonRaceResult.from_json(json_data=c["result"]),
                start=start_type.PersonRaceStart.from_json(json_data=c["start"]),
                club_id=c["club_id"],
                club_name=c["club_name"],
            )
        else:
            raise KeyError

    def add_entry(
        self,
        event_id: int,
        competitor_id: Optional[int],
        first_name: str,
        last_name: str,
        gender: str,
        year: Optional[int],
        class_id: int,
        club_id: Optional[int],
        not_competing: bool,
        chip: str,
        fields: dict[int, str],
        status: result_type.ResultStatus,
        start_time: Optional[datetime.datetime],
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        if competitor_id is None:
            for com in self.get_competitors():
                if com.first_name == first_name and com.last_name == last_name:
                    competitor_id = com.id
                    if gender == "":
                        gender = com.gender
                    if year is None:
                        year = com.year
                    if chip == "":
                        chip = com.chip
                    if club_id is None:
                        club_id = com.club_id
                    break
            else:
                competitor_id = self.add_competitor(
                    first_name=first_name,
                    last_name=last_name,
                    club_id=club_id,
                    gender=gender,
                    year=year,
                    chip=chip,
                )

        competitor = self.get_competitor(id=competitor_id)
        self.update_competitor(
            id=competitor.id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            year=year,
            club_id=(competitor.club_id if competitor.club_id is not None else club_id),
            chip=competitor.chip if competitor.chip != "" else chip,
        )

        # check if competitor is already entered for this event
        entry_ids = self.get_entry_ids_by_competitor(
            event_id=event_id,
            competitor_id=competitor_id,
        )
        if entry_ids != []:
            raise ConstraintError("Competitor already registered for this event")

        cur = self.db.execute(
            """
            INSERT into entries (
                event_id,
                competitor_id,
                class_id,
                club_id,
                not_competing,
                result,
                start,
                chip,
                fields
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event_id,
                competitor_id,
                class_id,
                club_id,
                not_competing,
                result_type.PersonRaceResult(status=status).to_json(),
                start_type.PersonRaceStart(start_time=start_time).to_json(),
                chip,
                json.dumps(fields),
            ),
        )
        return cur.lastrowid

    def add_entry_result(
        self,
        event_id: int,
        chip: str,
        start_time: Optional[datetime.datetime],
        result: result_type.PersonRaceResult,
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        cur = self.db.execute(
            """
            INSERT into entries (
                event_id,
                competitor_id,
                class_id,
                club_id,
                not_competing,
                result,
                start,
                chip,
                fields
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event_id,
                None,
                None,
                None,
                False,
                result.to_json(),
                start_type.PersonRaceStart(start_time=start_time).to_json(),
                chip,
                json.dumps({}),
            ),
        )
        return cur.lastrowid

    def update_entry(
        self,
        id: int,
        first_name: str,
        last_name: str,
        gender: str,
        year: Optional[int],
        class_id: int,
        club_id: Optional[int],
        not_competing: bool,
        chip: str,
        fields: dict[int, str],
        status: result_type.ResultStatus,
        start_time: Optional[datetime.datetime],
    ) -> None:
        entry = self.get_entry(id=id)
        competitor = self.get_competitor(id=entry.competitor_id)
        self.update_competitor(
            id=competitor.id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            year=year,
            club_id=competitor.club_id,
            chip=competitor.chip,
        )

        result = entry.result
        result.status = status
        start = entry.start
        start.start_time = start_time
        cur = self.db.execute(
            """
            UPDATE entries SET
                class_id=?,
                club_id=?,
                not_competing=?,
                chip=?,
                fields=?,
                result=?,
                start=?
            WHERE id=?""",
            (
                class_id,
                club_id,
                not_competing,
                chip,
                json.dumps(fields),
                result.to_json(),
                start.to_json(),
                id,
            ),
        )
        if cur.rowcount == 0:
            raise KeyError

    def update_entry_result(
        self,
        id: int,
        chip: str,
        start_time: Optional[datetime.datetime],
        result: result_type.PersonRaceResult,
    ) -> None:
        entry = self.get_entry(id=id)
        start = entry.start
        start.start_time = start_time
        cur = self.db.execute(
            """
            UPDATE entries SET
                chip=?,
                result=?,
                start=?
            WHERE id=?""",
            (
                chip,
                result.to_json(),
                start.to_json(),
                id,
            ),
        )
        if cur.rowcount == 0:
            raise KeyError

    def delete_entries(self, event_id: int) -> None:
        self.db.execute(
            "DELETE FROM entries WHERE event_id=?",
            (event_id,),
        )

    def delete_entry(self, id: int) -> None:
        self.db.execute(
            "DELETE FROM entries WHERE id=?",
            (id,),
        )

    def import_entries(self, event_id: int, entries: list[dict]) -> None:
        # check if the event still exists
        self.get_event(id=event_id)

        list_of_entries = []
        for c in entries:
            class_id = None
            class_ = None
            for cla in self.get_classes(event_id=event_id):
                if cla.name == c["class_"]:
                    class_id = cla.id
                    class_ = cla
                    break
            else:
                class_id = self.add_class(
                    event_id=event_id,
                    name=c["class_"],
                    short_name=None,
                    course_id=None,
                    params=ClassParams(),
                )

            club_id = None
            if c["club"]:
                for clb in self.get_clubs():
                    if clb.name == c["club"]:
                        club_id = clb.id
                        break
                else:
                    club_id = self.add_club(c["club"])

            gender = c["gender"] if "gender" in c else ""
            year = c["year"] if "year" in c else None
            try:
                competitor = self.get_competitor_by_name(
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                )
            except KeyError:
                competitor_id = self.add_competitor(
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                    club_id=club_id,
                    gender=gender,
                    year=year,
                    chip=c["chip"] if "chip" in c else "",
                )
            else:
                competitor_id = competitor.id
                # update gender and year in competitor
                gender = gender if gender != "" else competitor.gender
                year = year if year is not None else competitor.year
                if gender != competitor.gender or year != competitor.year:
                    self.update_competitor(
                        id=competitor.id,
                        first_name=competitor.first_name,
                        last_name=competitor.last_name,
                        club_id=competitor.club_id,
                        gender=gender,
                        year=year,
                        chip=competitor.chip,
                    )

            # update result
            if c["result"].has_punches():
                try:
                    course_id = class_["course_id"]
                    class_params = class_["params"]
                    controls = self.get_course(id=course_id).controls
                except Exception:
                    class_params = ClassParams()
                    controls = []
                c["result"].compute_result(
                    controls=controls,
                    class_params=class_params,
                    start_time=c["result"].start_time,
                    year=year,
                    gender=gender if gender != "" else None,
                )

            try:
                entry = self.get_entry_by_name(
                    event_id=event_id,
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                )
                fields = entry.fields
                if "fields" in c:
                    fields = copy.deepcopy(c["fields"])
                result = entry.result
                if "result" in c:
                    result = copy.deepcopy(c["result"])
                start = entry.start
                if "start" in c:
                    start = copy.deepcopy(c["start"])

                self.db.execute(
                    """
                    UPDATE entries SET
                        class_id=?,
                        club_id=?,
                        not_competing=?,
                        chip=?,
                        fields=?,
                        result=?,
                        start=?
                    WHERE id=?""",
                    (
                        class_id,
                        club_id,
                        (
                            c["not_competing"]
                            if "not_competing" in c
                            else entry.not_competing
                        ),
                        c["chip"] if "chip" in c else entry.chip,
                        json.dumps(fields),
                        result.to_json(),
                        start.to_json(),
                        entry.id,
                    ),
                )
            except KeyError:
                if "result" in c:
                    result = copy.deepcopy(c["result"])
                else:
                    result = result_type.PersonRaceResult()
                if "start" in c:
                    start = copy.deepcopy(c["start"])
                else:
                    start = start_type.PersonRaceStart()
                list_of_entries.append(
                    (
                        event_id,
                        competitor_id,
                        class_id,
                        club_id,
                        c["not_competing"] if "not_competing" in c else False,
                        result.to_json(),
                        start.to_json(),
                        c["chip"] if "chip" in c else "",
                        json.dumps(c["fields"] if "fields" in c else {}),
                    )
                )

        # check that each competitor has only one entry
        competitor_ids: set[int] = set()
        for e in list_of_entries:
            if e[1] in competitor_ids:
                raise ConstraintError("Competitor already registered for this event")
            else:
                competitor_ids.add(e[1])

        if list_of_entries:
            self.db.executemany(
                """
                INSERT into entries (
                    event_id,
                    competitor_id,
                    class_id,
                    club_id,
                    not_competing,
                    result,
                    start,
                    chip,
                    fields
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                list_of_entries,
            )

    def get_events(self) -> list[EventType]:
        values = self.db.execute(
            """
            SELECT
                id,
                name,
                date,
                key,
                publish,
                series,
                fields,
                streaming_address,
                streaming_key,
                streaming_enabled
            FROM events
            ORDER BY events.name ASC""",
        )
        events = []
        for e in values:
            streaming_enabled = None
            if e["streaming_enabled"] is not None:
                streaming_enabled = bool(e["streaming_enabled"])

            events.append(
                EventType(
                    id=e["id"],
                    name=e["name"],
                    date=datetime.datetime.strptime(e["date"], "%Y-%m-%d").date(),
                    key=e["key"],
                    publish=bool(e["publish"]),
                    series=e["series"],
                    fields=json.loads(e["fields"]),
                    streaming_address=e["streaming_address"],
                    streaming_key=e["streaming_key"],
                    streaming_enabled=streaming_enabled,
                )
            )
        return events

    def get_event(self, id: int) -> EventType:
        cur = self.db.execute(
            """
            SELECT
                id,
                name,
                date,
                key,
                publish,
                series,
                fields,
                streaming_address,
                streaming_key,
                streaming_enabled
            FROM events WHERE id=?""",
            (id,),
        )
        e = cur.fetchone()
        if e:
            streaming_enabled = None
            if e["streaming_enabled"] is not None:
                streaming_enabled = bool(e["streaming_enabled"])

            return EventType(
                id=e["id"],
                name=e["name"],
                date=datetime.datetime.strptime(e["date"], "%Y-%m-%d").date(),
                key=e["key"],
                publish=bool(e["publish"]),
                series=e["series"],
                fields=json.loads(e["fields"]),
                streaming_address=e["streaming_address"],
                streaming_key=e["streaming_key"],
                streaming_enabled=streaming_enabled,
            )
        else:
            raise EventNotFoundError

    def add_event(
        self,
        name: str,
        date: datetime.date,
        key: Optional[str],
        publish: bool,
        series: Optional[str],
        fields: list[str],
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ) -> int:
        try:
            cur = self.db.execute(
                """
                INSERT into events (
                    name,
                    date,
                    key,
                    publish,
                    series,
                    fields,
                    streaming_address,
                    streaming_key,
                    streaming_enabled
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    date.isoformat(),
                    key,
                    publish,
                    series,
                    json.dumps(fields),
                    streaming_address,
                    streaming_key,
                    streaming_enabled,
                ),
            )
            return cur.lastrowid

        except sqlite3.IntegrityError:
            raise ConstraintError("Event or event key already exist")

    def update_event(
        self,
        id: int,
        name: str,
        date: datetime.date,
        key: Optional[str],
        publish: bool,
        series: Optional[str],
        fields: list[str],
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ) -> None:
        try:
            cur = self.db.execute(
                """
                UPDATE events SET
                    name=?,
                    date=?,
                    key=?,
                    publish=?,
                    series=?,
                    fields=?,
                    streaming_address=?,
                    streaming_key=?,
                    streaming_enabled=?
                WHERE id=?""",
                (
                    name,
                    date.isoformat(),
                    key,
                    publish,
                    series,
                    json.dumps(fields),
                    streaming_address,
                    streaming_key,
                    streaming_enabled,
                    id,
                ),
            )
            if cur.rowcount == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Event or event key already exist")

    def delete_event(self, id: int) -> None:
        self.db.execute(
            "DELETE FROM events WHERE id=?",
            (id,),
        )

    def get_series_settings(self) -> series_type.Settings:
        cur = self.db.execute(
            """
            SELECT
                name,
                nr_of_best_results,
                mode,
                maximum_points,
                decimal_places
            FROM settings""",
        )
        s = cur.fetchone()
        if s:
            return series_type.Settings(
                name=s["name"],
                nr_of_best_results=s["nr_of_best_results"],
                mode=s["mode"],
                maximum_points=s["maximum_points"],
                decimal_places=s["decimal_places"],
            )
        else:
            return series_type.Settings()

    def update_series_settings(self, settings: series_type.Settings) -> None:
        cur = self.db.execute(
            """
            UPDATE settings SET
                name=?,
                nr_of_best_results=?,
                mode=?,
                maximum_points=?,
                decimal_places=?""",
            (
                settings.name,
                settings.nr_of_best_results,
                settings.mode,
                settings.maximum_points,
                settings.decimal_places,
            ),
        )
        if cur.rowcount == 0:
            cur = self.db.execute(
                """
                INSERT into settings (
                    name,
                    nr_of_best_results,
                    mode,
                    maximum_points,
                    decimal_places
                )
                VALUES(?, ?, ?, ?, ?)""",
                (
                    settings.name,
                    settings.nr_of_best_results,
                    settings.mode,
                    settings.maximum_points,
                    settings.decimal_places,
                ),
            )
            return cur.lastrowid

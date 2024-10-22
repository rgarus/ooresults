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
import copy
import logging
import sqlite3
import datetime
from typing import Dict
from typing import List
from typing import Optional

import web
import web.db

from ooresults.repo.repo import Repo
from ooresults.repo.repo import ClassUsedError
from ooresults.repo.repo import CourseUsedError
from ooresults.repo.repo import ClubUsedError
from ooresults.repo.repo import CompetitorUsedError
from ooresults.repo.repo import EventNotFoundError
from ooresults.repo.repo import ConstraintError
from ooresults.repo.repo import OperationalError
from ooresults.repo.repo import TransactionMode
from ooresults.repo.update import update_tables
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.class_type import ClassType
from ooresults.repo.club_type import ClubType
from ooresults.repo.competitor_type import CompetitorType
from ooresults.repo.course_type import CourseType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.event_type import EventType
from ooresults.repo import result_type
from ooresults.repo import series_type
from ooresults.repo import start_type


class SqliteRepo(Repo):
    def __init__(self, db: str = "ooresults.sqlite"):
        self.db = web.database(dbn="sqlite", db=db)

        # sqlite3.register_adapter(bool, int)
        # sqlite3.register_converter("BOOLEAN", lambda v: v != '0')

        values = list(
            self.db.query(
                "SELECT name FROM sqlite_schema WHERE type="
                + web.db.sqlquote("table")
                + " AND name="
                + web.db.sqlquote("version")
                + ";"
            )
        )

        if not values:
            # create and initialize database tables
            self.db.query("CREATE TABLE version (value INTEGER PRIMARY KEY);")
            self.db.query(
                "CREATE TABLE classes ("
                "id INTEGER PRIMARY KEY,"
                "event_id INTEGER NOT NULL,"
                "name TEXT NOT NULL,"
                "short_name TEXT,"
                "course_id INTEGER,"
                "params BLOB NOT NULL,"
                "UNIQUE (event_id, name)"
                ");"
            )
            self.db.query(
                "CREATE TABLE courses ("
                "id INTEGER PRIMARY KEY,"
                "event_id INTEGER NOT NULL,"
                "name TEXT NOT NULL,"
                "length FLOAT,"
                "climb FLOAT,"
                "controls BLOB NOT NULL,"
                "UNIQUE (event_id, name)"
                ");"
            )
            self.db.query(
                "CREATE TABLE clubs (" "id INTEGER PRIMARY KEY," "name TEXT UNIQUE" ");"
            )
            self.db.query(
                "CREATE TABLE competitors ("
                "id INTEGER PRIMARY KEY,"
                "first_name TEXT NOT NULL,"
                "last_name TEXT NOT NULL,"
                "club_id INTEGER,"
                "gender TEXT,"
                "year INTEGER,"
                "chip TEXT,"
                "UNIQUE (first_name, last_name)"
                ");"
            )
            self.db.query(
                "CREATE TABLE events ("
                "id INTEGER PRIMARY KEY,"
                "name TEXT NOT NULL UNIQUE,"
                "date TEXT,"
                "key TEXT UNIQUE,"
                "publish BOOL NOT NULL,"
                "series TEXT,"
                "fields BLOB NOT NULL,"
                "streaming_address TEXT,"
                "streaming_key TEXT,"
                "streaming_enabled BOOL"
                ");"
            )
            self.db.query(
                "CREATE TABLE entries ("
                "id INTEGER PRIMARY KEY,"
                "event_id INTEGER NOT NULL,"
                "competitor_id INTEGER,"
                "class_id INTEGER,"
                "club_id INTEGER,"
                "not_competing BOOL NOT NULL,"
                "result BLOB NOT NULL,"
                "start BLOB NOT NULL,"
                "chip TEXT,"
                "fields BLOB NOT NULL,"
                "UNIQUE (event_id, competitor_id)"
                ");"
            )
            self.db.query(
                "CREATE TABLE settings ("
                "name TEXT NOT NULL,"
                "nr_of_best_results INTEGER,"
                "mode TEXT NOT NULL,"
                "maximum_points INTEGER NOT NULL,"
                "decimal_places INTEGER NOT NULL"
                ");"
            )

            t = self.db.transaction()
            self.db.ctx.db.execute("BEGIN EXCLUSIVE TRANSACTION;")
            self.db.insert("version", value=update_tables.VERSION)
            t.commit()
            logging.info(f"DB version initialized to {update_tables.VERSION}")

        else:
            update_tables.update_tables(db=self.db, path=db)

    def start_transaction(self, mode: TransactionMode = TransactionMode.DEFERRED):
        self.t = self.db.transaction()
        try:
            self.db.ctx.db.execute(f"BEGIN {mode.value} TRANSACTION;")
        except sqlite3.OperationalError as e:
            raise OperationalError(str(e))

    def commit(self):
        self.t.commit()

    def rollback(self):
        self.t.rollback()

    def get_classes(self, event_id: int) -> List[ClassInfoType]:
        values = self.db.query(
            "SELECT "
            "classes.id,"
            "classes.name,"
            "classes.short_name,"
            "courses.id,"
            "courses.name,"
            "courses.length,"
            "courses.climb,"
            "courses.controls,"
            "classes.params "
            "FROM classes "
            "LEFT JOIN courses ON classes.course_id = courses.id "
            "WHERE classes.event_id = " + web.db.sqlquote(event_id) + " "
            "ORDER BY classes.name ASC;"
        )
        values.names[values.names.index("id", 1)] = "course_id"
        values.names[values.names.index("name", 2)] = "course_name"
        values.names[values.names.index("length", 1)] = "course_length"
        values.names[values.names.index("climb", 1)] = "course_climb"

        classes = []
        for c in values:
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
        values = self.db.where("classes", id=id)
        if values:
            c = values[0]
            return ClassType(
                id=c.id,
                event_id=c.event_id,
                name=c.name,
                short_name=c.short_name,
                course_id=c.course_id,
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
            return self.db.insert(
                "classes",
                event_id=event_id,
                name=name,
                short_name=short_name,
                course_id=course_id,
                params=params.to_json(),
            )
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
            nr_of_rows = self.db.update(
                "classes",
                where="id=" + web.db.sqlquote(id),
                name=name,
                short_name=short_name,
                course_id=course_id,
                params=params.to_json(),
            )
            if nr_of_rows == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Class already exist")

    def delete_classes(self, event_id: int):
        if self.db.where("entries", event_id=event_id).first() is None:
            self.db.delete("classes", where="event_id=" + web.db.sqlquote(event_id))
        else:
            raise ClassUsedError

    def delete_class(self, id: int):
        if self.db.where("entries", class_id=id).first() is None:
            self.db.delete("classes", where="id=" + web.db.sqlquote(id))
        else:
            raise ClassUsedError

    def get_courses(self, event_id: int) -> List[CourseType]:
        values = self.db.select(
            "courses",
            where="event_id=" + web.db.sqlquote(event_id),
            order="name ASC",
        )
        courses = []
        for c in values:
            courses.append(
                CourseType(
                    id=c.id,
                    event_id=c.event_id,
                    name=c.name,
                    length=c.length,
                    climb=c.climb,
                    controls=json.loads(c.controls),
                )
            )
        return courses

    def get_course(self, id: int) -> CourseType:
        values = self.db.where("courses", id=id)
        if values:
            c = values[0]
            return CourseType(
                id=c.id,
                event_id=c.event_id,
                name=c.name,
                length=c.length,
                climb=c.climb,
                controls=json.loads(c.controls),
            )
        else:
            raise KeyError

    def add_course(
        self,
        event_id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: List[str],
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        try:
            return self.db.insert(
                "courses",
                event_id=event_id,
                name=name,
                length=length,
                climb=climb,
                controls=json.dumps(controls),
            )
        except sqlite3.IntegrityError:
            raise ConstraintError("Course already exist")

    def update_course(
        self,
        id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: List[str],
    ):
        try:
            nr_of_rows = self.db.update(
                "courses",
                where="id=" + web.db.sqlquote(id),
                name=name,
                length=length,
                climb=climb,
                controls=json.dumps(controls),
            )
            if nr_of_rows == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Course already exist")

    def delete_courses(self, event_id: int):
        if (
            self.db.select(
                "classes",
                where="event_id="
                + web.db.sqlquote(event_id)
                + " and course_id is not null",
            ).first()
            is None
        ):
            self.db.delete("courses", where="event_id=" + web.db.sqlquote(event_id))
        else:
            raise CourseUsedError

    def delete_course(self, id: int):
        if self.db.where("classes", course_id=id).first() is None:
            self.db.delete("courses", where="id=" + web.db.sqlquote(id))
        else:
            raise CourseUsedError

    def get_clubs(self) -> List[ClubType]:
        values = self.db.select("clubs", order="name ASC")
        clubs = []
        for c in values:
            clubs.append(
                ClubType(
                    id=c.id,
                    name=c.name,
                )
            )
        return clubs

    def get_club(self, id: int) -> ClubType:
        values = self.db.where("clubs", id=id)
        if values:
            c = values[0]
            return ClubType(
                id=c.id,
                name=c.name,
            )
        else:
            raise KeyError

    def add_club(self, name: str) -> int:
        try:
            return self.db.insert("clubs", name=name)
        except sqlite3.IntegrityError:
            raise ConstraintError("Club already exist")

    def update_club(self, id: int, name: str) -> None:
        try:
            nr_of_rows = self.db.update(
                "clubs", where="id=" + web.db.sqlquote(id), name=name
            )
            if nr_of_rows == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Club already exist")

    def delete_club(self, id: int) -> None:
        if (
            self.db.where("competitors", club_id=id).first() is None
            and self.db.where("entries", club_id=id).first() is None
        ):
            self.db.delete("clubs", where="id=" + web.db.sqlquote(id))
        else:
            raise ClubUsedError

    def get_competitors(self) -> List[CompetitorType]:
        values = self.db.query(
            "SELECT competitors.*, clubs.* "
            "FROM competitors "
            "LEFT JOIN clubs ON competitors.club_id = clubs.id "
            "ORDER BY competitors.last_name ASC, competitors.first_name ASC;"
        )
        values.names[values.names.index("id", 1)] = "club_id"
        values.names[values.names.index("name")] = "club_name"

        competitors = []
        for c in values:
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
        values = self.db.query(
            "SELECT competitors.*, clubs.* "
            "FROM competitors "
            "LEFT JOIN clubs ON competitors.club_id = clubs.id "
            "WHERE competitors.id = " + web.db.sqlquote(id) + ";"
        )
        values.names[values.names.index("id", 1)] = "club_id"
        values.names[values.names.index("name")] = "club_name"

        if values:
            c = values[0]
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
        values = self.db.query(
            "SELECT competitors.*, clubs.* "
            "FROM competitors "
            "LEFT JOIN clubs ON competitors.club_id = clubs.id "
            "WHERE competitors.first_name = "
            + web.db.sqlquote(first_name)
            + "AND competitors.last_name = "
            + web.db.sqlquote(last_name)
            + ";"
        )
        values.names[values.names.index("id", 1)] = "club_id"
        values.names[values.names.index("name")] = "club_name"

        if values:
            c = values[0]
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
            return self.db.insert(
                "competitors",
                first_name=first_name,
                last_name=last_name,
                club_id=club_id,
                gender=gender,
                year=year,
                chip=chip,
            )
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
            nr_of_rows = self.db.update(
                "competitors",
                where="id=" + web.db.sqlquote(id),
                first_name=first_name,
                last_name=last_name,
                club_id=club_id,
                gender=gender,
                year=year,
                chip=chip,
            )
            if nr_of_rows == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Competitor already exist")

    def delete_competitor(self, id: int) -> None:
        if self.db.where("entries", competitor_id=id).first() is None:
            self.db.delete("competitors", where="id=" + web.db.sqlquote(id))
        else:
            raise CompetitorUsedError

    def import_competitors(self, competitors: List[Dict]) -> None:
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
                    {
                        "last_name": c["last_name"],
                        "first_name": c["first_name"],
                        "club_id": club_id,
                        "gender": c["gender"] if "gender" in c else "",
                        "year": c["year"] if "year" in c else "",
                        "chip": c["chip"] if "chip" in c else "",
                    }
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

        self.db.supports_multiple_insert = True
        if list_of_competitors:
            self.db.multiple_insert("competitors", list_of_competitors)

    def get_entries(self, event_id: int) -> List[EntryType]:
        values = self.db.query(
            "SELECT "
            "entries.id,"
            "entries.event_id,"
            "competitors.id,"
            "competitors.first_name,"
            "competitors.last_name,"
            "competitors.gender,"
            "competitors.year,"
            "entries.class_id,"
            "classes.name,"
            "entries.not_competing,"
            "entries.chip,"
            "entries.fields,"
            "entries.result,"
            "entries.start,"
            "entries.club_id,"
            "clubs.name "
            "FROM entries "
            "LEFT JOIN competitors ON entries.competitor_id = competitors.id "
            "LEFT JOIN classes ON entries.class_id = classes.id "
            "LEFT JOIN clubs ON entries.club_id = clubs.id "
            "WHERE entries.event_id = " + web.db.sqlquote(event_id) + " "
            "ORDER BY competitors.last_name ASC, competitors.first_name ASC, entries.chip ASC;"
        )
        values.names[values.names.index("id", 1)] = "competitor_id"
        values.names[values.names.index("name")] = "class_name"
        values.names[values.names.index("name")] = "club_name"

        entries = []
        for c in values:
            fields = {int(key): value for key, value in json.loads(c.fields).items()}

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
                    not_competing=bool(c.not_competing),
                    chip=c["chip"],
                    fields=fields,
                    result=result_type.PersonRaceResult.from_json(json_data=c.result),
                    start=start_type.PersonRaceStart.from_json(json_data=c.start),
                    club_id=c["club_id"],
                    club_name=c["club_name"],
                )
            )
        return entries

    def get_entry(self, id: int) -> EntryType:
        values = self.db.query(
            "SELECT "
            "entries.id,"
            "entries.event_id,"
            "competitors.id,"
            "competitors.first_name,"
            "competitors.last_name,"
            "competitors.gender,"
            "competitors.year,"
            "classes.id,"
            "classes.name,"
            "clubs.id,"
            "clubs.name,"
            "entries.not_competing,"
            "entries.chip,"
            "entries.fields,"
            "entries.result,"
            "entries.start "
            "FROM entries "
            "LEFT JOIN competitors ON entries.competitor_id = competitors.id "
            "LEFT JOIN classes ON entries.class_id = classes.id "
            "LEFT JOIN clubs ON entries.club_id = clubs.id "
            "WHERE entries.id = " + web.db.sqlquote(id) + ";"
        )
        values.names[values.names.index("id", 1)] = "competitor_id"
        values.names[values.names.index("id", 1)] = "class_id"
        values.names[values.names.index("id", 1)] = "club_id"
        values.names[values.names.index("name")] = "class_name"
        values.names[values.names.index("name")] = "club_name"

        if values:
            c = values[0]
            fields = {int(key): value for key, value in json.loads(c.fields).items()}

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
                not_competing=bool(c.not_competing),
                chip=c["chip"],
                fields=fields,
                result=result_type.PersonRaceResult.from_json(json_data=c.result),
                start=start_type.PersonRaceStart.from_json(json_data=c.start),
                club_id=c["club_id"],
                club_name=c["club_name"],
            )
        else:
            raise KeyError

    def get_entry_by_name(
        self, event_id: int, first_name: str, last_name: str
    ) -> EntryType:
        values = self.db.query(
            "SELECT "
            "entries.id,"
            "entries.event_id,"
            "competitors.id,"
            "competitors.first_name,"
            "competitors.last_name,"
            "competitors.gender,"
            "competitors.year,"
            "classes.id,"
            "classes.name,"
            "clubs.id,"
            "clubs.name,"
            "entries.not_competing,"
            "entries.chip,"
            "entries.fields,"
            "entries.result,"
            "entries.start "
            "FROM entries "
            "LEFT JOIN competitors ON entries.competitor_id = competitors.id "
            "LEFT JOIN classes ON entries.class_id = classes.id "
            "LEFT JOIN clubs ON entries.club_id = clubs.id "
            "WHERE entries.event_id = " + web.db.sqlquote(event_id) + " AND "
            "competitors.first_name = " + web.db.sqlquote(first_name) + " AND "
            "competitors.last_name = " + web.db.sqlquote(last_name) + ";"
        )
        values.names[values.names.index("id", 1)] = "competitor_id"
        values.names[values.names.index("id", 1)] = "class_id"
        values.names[values.names.index("id", 1)] = "club_id"
        values.names[values.names.index("name")] = "class_name"
        values.names[values.names.index("name")] = "club_name"

        if values:
            c = values[0]
            fields = {int(key): value for key, value in json.loads(c.fields).items()}

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
                not_competing=bool(c.not_competing),
                chip=c["chip"],
                fields=fields,
                result=result_type.PersonRaceResult.from_json(json_data=c.result),
                start=start_type.PersonRaceStart.from_json(json_data=c.start),
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
        fields: Dict[int, str],
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
        try:
            competitor = self.get_competitor(id=competitor_id)
            self.update_competitor(
                id=competitor.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                year=year,
                club_id=competitor.club_id
                if competitor.club_id is not None
                else club_id,
                chip=competitor.chip if competitor.chip != "" else chip,
            )
            return self.db.insert(
                "entries",
                event_id=event_id,
                competitor_id=competitor_id,
                class_id=class_id,
                club_id=club_id,
                not_competing=not_competing,
                result=result_type.PersonRaceResult(status=status).to_json(),
                start=start_type.PersonRaceStart(start_time=start_time).to_json(),
                chip=chip,
                fields=json.dumps(fields),
            )
        except sqlite3.IntegrityError:
            raise ConstraintError("Competitor already registered for this event")

    def add_entry_result(
        self,
        event_id: int,
        chip: str,
        start_time: Optional[datetime.datetime],
        result: result_type.PersonRaceResult,
    ) -> int:
        # check if the event still exists
        self.get_event(id=event_id)

        try:
            return self.db.insert(
                "entries",
                event_id=event_id,
                competitor_id=None,
                class_id=None,
                club_id=None,
                not_competing=False,
                result=result.to_json(),
                start=start_type.PersonRaceStart(start_time=start_time).to_json(),
                chip=chip,
                fields=json.dumps({}),
            )
        except sqlite3.IntegrityError:
            raise ConstraintError("Competitor already registered for this event")

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
        fields: Dict[int, str],
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
        self.db.update(
            "entries",
            where="id=" + web.db.sqlquote(id),
            class_id=class_id,
            club_id=club_id,
            not_competing=not_competing,
            chip=chip,
            fields=json.dumps(fields),
            result=result.to_json(),
            start=start.to_json(),
        )

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
        self.db.update(
            "entries",
            where="id=" + web.db.sqlquote(id),
            chip=chip,
            result=result.to_json(),
            start=start.to_json(),
        )

    def delete_entries(self, event_id: int) -> None:
        self.db.delete("entries", where="event_id=" + web.db.sqlquote(event_id))

    def delete_entry(self, id: int) -> None:
        self.db.delete("entries", where="id=" + web.db.sqlquote(id))

    def import_entries(self, event_id: int, entries: List[Dict]) -> None:
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
                except:
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
                self.db.update(
                    "entries",
                    where="id=" + web.db.sqlquote(entry.id),
                    class_id=class_id,
                    club_id=club_id,
                    not_competing=c["not_competing"]
                    if "not_competing" in c
                    else entry.not_competing,
                    chip=c["chip"] if "chip" in c else entry.chip,
                    fields=json.dumps(fields),
                    result=result.to_json(),
                    start=start.to_json(),
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
                    {
                        "event_id": event_id,
                        "competitor_id": competitor_id,
                        "class_id": class_id,
                        "club_id": club_id,
                        "not_competing": c["not_competing"]
                        if "not_competing" in c
                        else False,
                        "chip": c["chip"] if "chip" in c else "",
                        "fields": json.dumps(c["fields"] if "fields" in c else {}),
                        "result": result.to_json(),
                        "start": start.to_json(),
                    }
                )

        self.db.supports_multiple_insert = True
        for i in range(0, len(entries), 25):
            self.db.multiple_insert(
                "entries", list_of_entries[i : min(i + 25, len(entries))]
            )

    def get_events(self) -> List[EventType]:
        values = self.db.query(
            "SELECT "
            "events.id,"
            "events.name,"
            "events.date,"
            "events.key,"
            "events.publish,"
            "events.series,"
            "events.fields,"
            "events.streaming_address,"
            "events.streaming_key,"
            "events.streaming_enabled "
            "FROM events "
            "ORDER BY events.name ASC;"
        )
        events = []
        for e in values:
            streaming_enabled = None
            if e.streaming_enabled is not None:
                streaming_enabled = bool(e.streaming_enabled)

            events.append(
                EventType(
                    id=e.id,
                    name=e.name,
                    date=datetime.datetime.strptime(e.date, "%Y-%m-%d").date(),
                    key=e.key,
                    publish=bool(e.publish),
                    series=e.series,
                    fields=json.loads(e.fields),
                    streaming_address=e.streaming_address,
                    streaming_key=e.streaming_key,
                    streaming_enabled=streaming_enabled,
                )
            )
        return events

    def get_event(self, id: int) -> EventType:
        values = self.db.where("events", id=id)
        if values:
            e = values[0]
            streaming_enabled = None
            if e.streaming_enabled is not None:
                streaming_enabled = bool(e.streaming_enabled)

            return EventType(
                id=e.id,
                name=e.name,
                date=datetime.datetime.strptime(e.date, "%Y-%m-%d").date(),
                key=e.key,
                publish=bool(e.publish),
                series=e.series,
                fields=json.loads(e.fields),
                streaming_address=e.streaming_address,
                streaming_key=e.streaming_key,
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
        fields: List[str],
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ) -> int:
        try:
            return self.db.insert(
                "events",
                name=name,
                date=date.isoformat(),
                key=key,
                publish=publish,
                series=series,
                fields=json.dumps(fields),
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )

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
        fields: List[str],
        streaming_address: Optional[str] = None,
        streaming_key: Optional[str] = None,
        streaming_enabled: Optional[bool] = None,
    ) -> None:
        try:
            nr_of_rows = self.db.update(
                "events",
                where="id=" + web.db.sqlquote(id),
                name=name,
                date=date.isoformat(),
                key=key,
                publish=publish,
                series=series,
                fields=json.dumps(fields),
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )
            if nr_of_rows == 0:
                raise KeyError
        except sqlite3.IntegrityError:
            raise ConstraintError("Event or event key already exist")

    def delete_event(self, id: int) -> None:
        self.db.delete("events", where="id=" + web.db.sqlquote(id))

    def get_series_settings(self) -> series_type.Settings:
        values = self.db.query(
            "SELECT name, nr_of_best_results, mode, maximum_points, decimal_places FROM settings;"
        )
        if values:
            s = values[0]
            return series_type.Settings(
                name=s.name,
                nr_of_best_results=s.nr_of_best_results,
                mode=s.mode,
                maximum_points=s.maximum_points,
                decimal_places=s.decimal_places,
            )
        else:
            return series_type.Settings()

    def update_series_settings(self, settings: series_type.Settings) -> None:
        nr_of_rows = self.db.update(
            tables="settings",
            where="True",
            name=settings.name,
            nr_of_best_results=settings.nr_of_best_results,
            mode=settings.mode,
            maximum_points=settings.maximum_points,
            decimal_places=settings.decimal_places,
        )
        if nr_of_rows == 0:
            self.db.insert(
                tablename="settings",
                name=settings.name,
                nr_of_best_results=settings.nr_of_best_results,
                mode=settings.mode,
                maximum_points=settings.maximum_points,
                decimal_places=settings.decimal_places,
            )

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


import datetime
from enum import Enum
from typing import Optional

from ooresults.otypes import result_type
from ooresults.otypes import series_type
from ooresults.otypes import start_type
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.class_type import ClassType
from ooresults.otypes.club_type import ClubType
from ooresults.otypes.competitor_type import CompetitorBaseDataType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.otypes.course_type import CourseType
from ooresults.otypes.entry_type import EntryBaseDataType
from ooresults.otypes.entry_type import EntryType
from ooresults.otypes.event_type import EventType


class ClassUsedError(RuntimeError):
    pass


class CourseUsedError(RuntimeError):
    pass


class ClubUsedError(RuntimeError):
    pass


class CompetitorUsedError(RuntimeError):
    pass


class EventNotFoundError(RuntimeError):
    pass


class ConstraintError(RuntimeError):
    pass


class OperationalError(RuntimeError):
    pass


class DatabaseError(RuntimeError):
    pass


class TransactionMode(Enum):
    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


class Transaction:
    """Database transaction."""

    def __init__(self, db, mode: TransactionMode = TransactionMode.DEFERRED) -> None:
        self.db = db
        self.mode = mode

    def __enter__(self):
        self.db.start_transaction(mode=self.mode)
        return self

    def __exit__(self, exctype, excvalue, traceback) -> None:
        if exctype is not None:
            self.db.rollback()
        else:
            self.db.commit()


class Repo:
    def __init__(self) -> None:
        raise NotImplementedError

    def transaction(
        self, mode: TransactionMode = TransactionMode.DEFERRED
    ) -> Transaction:
        return Transaction(db=self, mode=mode)

    def start_transaction(
        self, mode: TransactionMode = TransactionMode.DEFERRED
    ) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def get_classes(self, event_id: int) -> list[ClassInfoType]:
        """Read all class records for an event from the ‘classes’ table.

        Possible errors:
        - Event does not exist
        """
        raise NotImplementedError

    def get_class(self, id: int) -> ClassType:
        """Read a class record from the ‘classes’ table.

        Possible errors:
        - Event does not exist
        - Class does not exist
        """
        raise NotImplementedError

    def add_class(
        self,
        event_id: int,
        name: str,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ) -> int:
        """Insert a class record into the 'classes' table.

        Possible errors:
        - Class already exists
        - Event does not exist
        - Course does not exist
        """
        raise NotImplementedError

    def update_class(
        self,
        id: int,
        name: str,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ) -> None:
        """Change a class record in the 'classes' table.

        Possible errors:
        - Class already exists
        - Event does not exist
        - Class does not exist
        - Course does not exist
        """
        raise NotImplementedError

    def delete_classes(self, event_id: int) -> None:
        """Delete all class records for an event from the ‘classes’ table.

        The statement is executed without error if no records are found
        (for example if the event has already been deleted).

        Possible errors:
        - One of the class records is used by an entry.
        """
        raise NotImplementedError

    def delete_class(self, id: int) -> None:
        """Delete a class record from the ‘classes’ table.

        The statement is executed without error if no record is found
        (for example if the class record has already been deleted).

        Possible errors:
        - Class used by an entry
        """
        raise NotImplementedError

    def get_courses(self, event_id: int) -> list[CourseType]:
        """Read all course records for an event from the 'courses' table.

        Possible errors:
        - Event does not exist
        """
        raise NotImplementedError

    def get_course(self, id: int) -> CourseType:
        """Read a course record from the 'courses' table.

        Possible errors:
        - Event does not exist
        - Course does not exist
        """
        raise NotImplementedError

    def add_course(
        self,
        event_id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: list[str],
    ) -> int:
        """Insert a course record into the 'courses' table.

        Possible errors:
        - Course already exists
        - Event does not exist
        """
        raise NotImplementedError

    def update_course(
        self,
        id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: list[str],
    ) -> None:
        """Change a course record in the 'courses' table.

        Possible errors:
        - Course already exists
        - Event does not exist
        - Course does not exist
        """
        raise NotImplementedError

    def delete_courses(self, event_id: int) -> None:
        """Delete all course records for an event from the ‘courses’ table.

        The statement is executed without error if no records are found
        (for example if the event has already been deleted).

        Possible errors:
        - One of the course records is used by a class.
        """
        raise NotImplementedError

    def delete_course(self, id: int) -> None:
        """Delete a course record from the ‘courses’ table.

        The statement is executed without error if no record is found
        (for example if the course record has already been deleted).

        Possible errors:
        - Course used by a class
        """
        raise NotImplementedError

    def get_clubs(self) -> list[ClubType]:
        """Read all club records from the 'clubs' table."""
        raise NotImplementedError

    def get_club(self, id: int) -> ClubType:
        """Read a club record from the 'clubs' table.

        Possible errors:
        - Club does not exist
        """
        raise NotImplementedError

    def add_club(self, name: str) -> int:
        """Insert a club record into the 'clubs' table.

        Possible errors:
        - Club already exists
        """
        raise NotImplementedError

    def update_club(self, id: int, name: str) -> None:
        """Change a club record in the 'clubs' table.

        Possible errors:
        - Club already exists
        - Club does not exist
        """
        raise NotImplementedError

    def delete_club(self, id: int) -> None:
        """Delete a club record from the ‘clubs’ table.

        The statement is executed without error if no record is found
        (for example if the club record has already been deleted).

        Possible errors:
        - Club used by an entry or by a competitor
        """
        raise NotImplementedError

    def get_competitors(self) -> list[CompetitorType]:
        """Read all competitor records from the 'competitors' table."""
        raise NotImplementedError

    def get_competitor(self, id: int) -> CompetitorType:
        """Read a competitor record from the 'competitors' table.

        Possible errors:
        - Competitor does not exist
        """
        raise NotImplementedError

    def get_competitor_by_name(
        self, first_name: str, last_name: str
    ) -> Optional[CompetitorType]:
        """Read a competitor record for a name from the 'competitors' table."""
        raise NotImplementedError

    def add_competitor(
        self,
        first_name: str,
        last_name: str,
        club_id: Optional[int],
        gender: str,
        year: Optional[int],
        chip: str,
    ) -> int:
        """Insert a competitor record into the 'competitors' table.

        Possible errors:
        - Competitor already exists
        - Club does not exist
        """
        raise NotImplementedError

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
        """Change a competitor record in the 'competitors' table.

        Possible errors:
        - Competitor already exists
        - Club does not exist
        """
        raise NotImplementedError

    def delete_competitor(self, id: int) -> None:
        """Delete a competitor record from the ‘competitors’ table.

        The statement is executed without error if no records are found
        (for example if the competitor has already been deleted).

        Possible errors:
        - Competitor used by an entry
        """
        raise NotImplementedError

    def add_many_competitors(
        self, list_of_competitors: list[CompetitorBaseDataType]
    ) -> None:
        """Insert multiple competitor records into the 'competitors' table.

        Possible errors:
        - Competitor already exists
        - Club does not exist
        """
        raise NotImplementedError

    def get_entries(self, event_id: int) -> list[EntryType]:
        """Read all entry records for an event from the 'entries' table.

        Possible errors:
        - Event does not exist
        """
        raise NotImplementedError

    def get_entry(self, id: int) -> EntryType:
        """Read an entry record from the 'entries' table.

        Possible errors:
        - Event does not exist
        - Entry does not exist
        """
        raise NotImplementedError

    def get_entry_ids_by_competitor(
        self, event_id: int, competitor_id: int
    ) -> list[int]:
        """Read all entry records for a competitor id from the 'entries' table."""
        raise NotImplementedError

    def get_entries_by_name(
        self, event_id: int, first_name: str, last_name: str
    ) -> list[EntryType]:
        """Read all entry records for a competitor name from the 'entries' table."""
        raise NotImplementedError

    def add_entry(
        self,
        event_id: int,
        competitor_id: int,
        class_id: int,
        club_id: Optional[int],
        not_competing: bool,
        chip: str,
        fields: dict[int, str],
        result: result_type.PersonRaceResult,
        start: start_type.PersonRaceStart,
    ) -> int:
        """Insert an entry record into the 'entries' table.

        Possible errors:
        - Event does not exist
        - Competitor does not exist
        - Club does not exist
        - Class does not exist
        """
        raise NotImplementedError

    def add_entry_result(
        self,
        event_id: int,
        chip: str,
        result: result_type.PersonRaceResult,
        start: start_type.PersonRaceStart,
    ) -> int:
        """Insert an entry record into the 'entries' table.

        Possible errors:
        - Event does not exist
        """
        raise NotImplementedError

    def update_entry(
        self,
        id: int,
        class_id: int,
        club_id: Optional[int],
        not_competing: bool,
        chip: str,
        fields: dict[int, str],
        result: result_type.PersonRaceResult,
        start: start_type.PersonRaceStart,
    ) -> None:
        """Change an entry record in the 'entries' table.

        Possible errors:
        - Entry already exists
        - Entry does not exist
        - Event does not exist
        - Competitor does not exist
        - Club does not exist
        - Class does not exist
        """
        raise NotImplementedError

    def update_entry_result(
        self,
        id: int,
        chip: str,
        result: result_type.PersonRaceResult,
        start: start_type.PersonRaceStart,
    ) -> None:
        """Change an entry record in the 'entries' table.

        Possible errors:
        - Entry does not exist
        - Competitor does not exist
        - Club does not exist
        - Class does not exist
        """
        raise NotImplementedError

    def delete_entries(self, event_id: int) -> None:
        """Delete all entry records for an event from the ‘entries’ table.

        The statement is executed without error if no records are found
        (for example if the event has already been deleted).
        """
        raise NotImplementedError

    def delete_entry(self, id: int) -> None:
        """Delete an entry record from the ‘entries’ table.

        The statement is executed without error if no record is found
        (for example if the entry record has already been deleted).
        """
        raise NotImplementedError

    def add_many_entries(self, list_of_entries: list[EntryBaseDataType]) -> None:
        """Insert multiple entry records into the 'entries' table.

        Possible errors:
        - Event does not exist
        - Course does not exist
        """
        raise NotImplementedError

    def get_events(self) -> list[EventType]:
        """Read all entry records from the 'events' table."""
        raise NotImplementedError

    def get_event(self, id: int) -> EventType:
        """Read an event record from the 'events' table.

        Possible errors:
        - Event does not exist
        """
        raise NotImplementedError

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
        """Insert an event record into the 'events' table.

        Possible errors:
        - Event already exists
        """
        raise NotImplementedError

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
        """Change an event record in the 'events' table.

        Possible errors:
        - Event already exists
        - Event does not exist
        """
        raise NotImplementedError

    def delete_event(self, id: int) -> None:
        """Delete an event record from the ‘events’ table.

        The statement is executed without error if no records are found
        (for example if the event has already been deleted).
        """
        raise NotImplementedError

    def get_series_settings(self) -> series_type.Settings:
        """Read a series record from the 'series' table."""
        raise NotImplementedError

    def update_series_settings(self, settings: series_type.Settings) -> None:
        """Change a series record in the 'series' table."""
        raise NotImplementedError

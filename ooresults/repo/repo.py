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
from typing import Dict
from typing import List

from ooresults.repo.class_params import ClassParams
from ooresults.repo.event_type import EventType
from ooresults.repo import result_type
from ooresults.repo import series_type


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


class TransactionMode(Enum):
    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


class Transaction:
    """Database transaction."""

    def __init__(self, db, mode: TransactionMode = TransactionMode.DEFERRED):
        self.db = db
        self.mode = mode

    def __enter__(self):
        self.db.start_transaction(mode=self.mode)
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if exctype is not None:
            self.db.rollback()
        else:
            self.db.commit()


class Repo:
    def __init__(self):
        raise NotImplementedError

    def transaction(
        self, mode: TransactionMode = TransactionMode.DEFERRED
    ) -> Transaction:
        return Transaction(db=self, mode=mode)

    def start_transaction(self, mode: str):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def get_classes(self, event_id: int):
        raise NotImplementedError

    def get_class(self, id):
        raise NotImplementedError

    def add_class(
        self,
        event_id: int,
        name: str,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ):
        raise NotImplementedError

    def update_class(
        self,
        id,
        name,
        short_name: Optional[str],
        course_id: Optional[int],
        params: ClassParams,
    ):
        raise NotImplementedError

    def delete_classes(self, event_id):
        raise NotImplementedError

    def delete_class(self, id):
        raise NotImplementedError

    def get_courses(self, event_id: int):
        raise NotImplementedError

    def get_course(self, id):
        raise NotImplementedError

    def add_course(
        self,
        event_id: int,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: List[str],
    ):
        raise NotImplementedError

    def update_course(
        self,
        id,
        name: str,
        length: Optional[float],
        climb: Optional[float],
        controls: List[str],
    ):
        raise NotImplementedError

    def delete_courses(self, event_id):
        raise NotImplementedError

    def delete_course(self, id):
        raise NotImplementedError

    def get_clubs(self):
        raise NotImplementedError

    def get_club(self, id):
        raise NotImplementedError

    def add_club(self, name: str):
        raise NotImplementedError

    def update_club(self, id, name: str):
        raise NotImplementedError

    def delete_club(self, id):
        raise NotImplementedError

    def get_competitors(self):
        raise NotImplementedError

    def get_competitor(self, id):
        raise NotImplementedError

    def add_competitor(
        self, first_name, last_name, club_id, gender, year: Optional[int], chip
    ):
        raise NotImplementedError

    def update_competitor(
        self, id, first_name, last_name, club_id, gender, year: Optional[int], chip
    ):
        raise NotImplementedError

    def delete_competitor(self, id):
        raise NotImplementedError

    def import_competitors(self, competitors):
        raise NotImplementedError

    def delete_entries(self, event_id):
        raise NotImplementedError

    def delete_entry(self, id):
        raise NotImplementedError

    def import_entries(self, event_id: int, entries: List[Dict]) -> None:
        raise NotImplementedError

    def get_entries(self, event_id):
        raise NotImplementedError

    def get_entry(self, id):
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    def add_entry_result(
        self,
        event_id: int,
        chip,
        start_time: Optional[datetime.datetime],
        result: result_type.PersonRaceResult,
    ) -> int:
        raise NotImplementedError

    def update_entry_result(
        self,
        id: int,
        chip,
        start_time: Optional[datetime.datetime],
        result: result_type.PersonRaceResult,
    ) -> None:
        raise NotImplementedError

    def get_events(self) -> List[EventType]:
        raise NotImplementedError

    def get_event(self, id: int) -> EventType:
        raise NotImplementedError

    def add_event(
        self,
        name: str,
        date: datetime.date,
        key: Optional[str],
        publish: bool,
        series: Optional[str],
        fields: List[str],
    ) -> int:
        raise NotImplementedError

    def update_event(
        self,
        id: int,
        name: str,
        date: datetime.date,
        key: Optional[str],
        publish: bool,
        series: Optional[str],
        fields: List[str],
    ) -> None:
        raise NotImplementedError

    def delete_event(self, id: int) -> None:
        raise NotImplementedError

    def get_series_settings(self) -> series_type.Settings:
        raise NotImplementedError

    def update_series_settings(self, settings: series_type.Settings) -> None:
        raise NotImplementedError

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


from typing import Dict
from typing import List
from typing import Optional

from ooresults import model
from ooresults.handler import cached_result
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.class_type import ClassType
from ooresults.repo.repo import TransactionMode


def get_classes(event_id: int) -> List[ClassInfoType]:
    with model.db.transaction():
        return model.db.get_classes(event_id=event_id)


def get_class(id: int) -> ClassType:
    with model.db.transaction():
        return model.db.get_class(id=id)


def import_classes(event_id: int, classes: List[Dict]) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_classes = model.db.get_classes(event_id=event_id)
        for c in classes:
            for cl in existing_classes:
                if cl.name == c["name"]:
                    model.db.update_class(
                        id=cl.id,
                        name=cl.name,
                        short_name=(
                            c["short_name"]
                            if c.get("short_name", None) is not None
                            else cl.short_name
                        ),
                        course_id=cl.course_id,
                        params=cl.params,
                    )
                    break
            else:
                model.db.add_class(
                    event_id=event_id,
                    name=c["name"],
                    short_name=c.get("short_name", None),
                    course_id=None,
                    params=ClassParams(),
                )

    cached_result.clear_cache(event_id=event_id)


def add_class(
    event_id: int,
    name: str,
    short_name: Optional[str],
    course_id: Optional[int],
    params: ClassParams,
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.add_class(
            event_id=event_id,
            name=name,
            short_name=short_name,
            course_id=course_id,
            params=params,
        )


def update_class(
    id: int,
    event_id: int,
    name: str,
    short_name: Optional[str],
    course_id: Optional[int],
    params: ClassParams,
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        # update class data
        try:
            model.db.update_class(
                id=id,
                name=name,
                short_name=short_name,
                course_id=course_id,
                params=params,
            )
        except KeyError:
            # distinguish between 'Event deleted' or 'Class deleted'
            model.db.get_event(id=event_id)
            raise

        # update results of the entries belonging to the modified class
        try:
            class_params = params
            controls = model.db.get_course(id=course_id).controls
        except Exception:
            class_params = ClassParams()
            controls = []

        entries = model.db.get_entries(event_id=event_id)
        for entry in entries:
            if entry.class_id == id:
                entry.result.compute_result(
                    controls=controls,
                    class_params=class_params,
                    start_time=entry.start.start_time,
                    year=entry.year,
                    gender=entry.gender if entry.gender != "" else None,
                )
                model.db.update_entry_result(
                    id=entry.id,
                    chip=entry.chip,
                    result=entry.result,
                    start_time=entry.start.start_time,
                )

    cached_result.clear_cache(event_id=event_id)


def delete_classes(event_id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_classes(event_id=event_id)


def delete_class(id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_class(id=id)

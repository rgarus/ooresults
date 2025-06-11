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
from ooresults.otypes.course_type import CourseType
from ooresults.repo.repo import TransactionMode


def get_courses(event_id: int) -> List[CourseType]:
    with model.db.transaction():
        return model.db.get_courses(event_id=event_id)


def get_course(id: int) -> CourseType:
    with model.db.transaction():
        return model.db.get_course(id=id)


def import_courses(
    event_id: int, courses: List[Dict], class_course: List[Dict]
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        existing_courses = model.db.get_courses(event_id=event_id)
        for c in courses:
            for co in existing_courses:
                if co.name == c["name"]:
                    model.db.update_course(
                        id=co.id,
                        name=co.name,
                        length=c.get("length", None),
                        climb=c.get("climb", None),
                        controls=c["controls"],
                    )
                    break
            else:
                model.db.add_course(
                    event_id=event_id,
                    name=c["name"],
                    length=c.get("length", None),
                    climb=c.get("climb", None),
                    controls=c["controls"],
                )
        existing_classes = model.db.get_classes(event_id=event_id)
        existing_courses = model.db.get_courses(event_id=event_id)
        for i in class_course:
            for co in existing_courses:
                if co.name == i.get("course_name", None):
                    for cl in existing_classes:
                        if cl.name == i["class_name"]:
                            model.db.update_class(
                                id=cl.id,
                                name=cl.name,
                                short_name=cl.short_name,
                                course_id=co.id,
                                params=cl.params,
                            )
                            break
                    else:
                        model.db.add_class(
                            event_id=event_id,
                            name=i["class_name"],
                            short_name=None,
                            course_id=co.id,
                            params=ClassParams(),
                        )
                    break
            else:
                if i["course_name"] is None:
                    for cl in existing_classes:
                        if cl.name == i["class_name"]:
                            model.db.update_class(
                                id=cl.id,
                                name=cl.name,
                                short_name=cl.short_name,
                                course_id=None,
                                params=cl.params,
                            )
                            break
                    else:
                        model.db.add_class(
                            event_id=event_id,
                            name=i["class_name"],
                            short_name=None,
                            course_id=None,
                            params=ClassParams(),
                        )

    cached_result.clear_cache(event_id=event_id)


def add_course(
    event_id: int,
    name: str,
    length: Optional[float],
    climb: Optional[float],
    controls: List[str],
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.add_course(
            event_id=event_id,
            name=name,
            length=length,
            climb=climb,
            controls=controls,
        )


def update_course(
    id: int,
    event_id: int,
    name: str,
    length: Optional[float],
    climb: Optional[float],
    controls: List[str],
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        # update course data
        try:
            model.db.update_course(
                id=id,
                name=name,
                length=length,
                climb=climb,
                controls=controls,
            )
        except KeyError:
            # distinguish between 'Event deleted' or 'Course deleted'
            model.db.get_event(id=event_id)
            raise

        # update results of the competitors belonging to a class using the modified course
        classes = model.db.get_classes(event_id=event_id)
        classes = [c for c in classes if c.course_id == id]

        entries = model.db.get_entries(event_id=event_id)
        for entry in entries:
            for class_ in classes:
                if entry.class_id == class_.id:
                    entry.result.compute_result(
                        controls=controls,
                        class_params=class_.params,
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
                    break

    cached_result.clear_cache(event_id=event_id)


def delete_courses(event_id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_courses(event_id=event_id)


def delete_course(id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_course(id=id)

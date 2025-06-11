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


from typing import List

from ooresults import model
from ooresults.handler import cached_result
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.repo.repo import TransactionMode


def get_competitors() -> List[CompetitorType]:
    with model.db.transaction():
        return model.db.get_competitors()


def get_competitor(id: int) -> CompetitorType:
    with model.db.transaction():
        return model.db.get_competitor(id=id)


def add_competitor(first_name, last_name, club_id, gender, year, chip):
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.add_competitor(
            first_name=first_name,
            last_name=last_name,
            club_id=club_id,
            gender=gender,
            year=year,
            chip=chip,
        )


def update_competitor(id, first_name, last_name, club_id, gender, year, chip):
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.update_competitor(
            id=id,
            first_name=first_name,
            last_name=last_name,
            club_id=club_id,
            gender=gender,
            year=year,
            chip=chip,
        )

    cached_result.clear_cache()


def delete_competitor(id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_competitor(id=id)


def import_competitors(competitors) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.import_competitors(competitors)

    cached_result.clear_cache()

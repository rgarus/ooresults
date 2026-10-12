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


from ooresults import model
from ooresults.model import cached_result
from ooresults.otypes.club_type import ClubType
from ooresults.repo.repo import TransactionMode


def get_clubs() -> list[ClubType]:
    """Get all clubs."""
    with model.db.transaction():
        return model.db.get_clubs()


def get_club(id: int) -> ClubType:
    """Get club.

    Possible errors:
    - Club does not exist
    """
    with model.db.transaction():
        return model.db.get_club(id=id)


def add_club(name: str) -> None:
    """Add a new club.

    Possible errors:
    - Club already exists
    """
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.add_club(name=name)


def update_club(id: int, name: str) -> None:
    """Update club.

    Possible errors:
    - Club already exists
    - Club does not exist
    """
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.update_club(id=id, name=name)

    cached_result.clear_cache()


def delete_club(id: int) -> None:
    """Delete a club.

    The function is executed without error if the club does not exist
    (for example if the club has already been deleted).

    Possible errors:
    - Club used by an entry or by a competitor
    """
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_club(id=id)

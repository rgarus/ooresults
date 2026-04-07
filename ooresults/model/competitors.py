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
from ooresults.otypes.competitor_type import CompetitorBaseDataType
from ooresults.otypes.competitor_type import CompetitorType
from ooresults.repo.repo import TransactionMode


def get_competitors() -> list[CompetitorType]:
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


def import_competitors(competitors: list[dict]) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        list_of_competitors = []
        for c in competitors:
            club_id = None
            if c["club"]:
                for clb in model.db.get_clubs():
                    if clb.name == c["club"]:
                        club_id = clb.id
                        break
                else:
                    club_id = model.db.add_club(name=c["club"])

            c_name = model.db.get_competitor_by_name(
                first_name=c["first_name"],
                last_name=c["last_name"],
            )
            if c_name:
                gender = c_name.gender
                if "gender" in c and c["gender"]:
                    gender = c["gender"]
                year = c_name.year
                if "year" in c and c["year"] is not None:
                    year = c["year"]
                chip = c_name.chip
                if "chip" in c and c["chip"]:
                    chip = c["chip"]
                model.db.update_competitor(
                    id=c_name.id,
                    first_name=c_name.first_name,
                    last_name=c_name.last_name,
                    club_id=c_name.club_id if club_id is None else club_id,
                    gender=gender,
                    year=year,
                    chip=chip,
                )
            else:

                list_of_competitors.append(
                    CompetitorBaseDataType(
                        first_name=c["first_name"],
                        last_name=c["last_name"],
                        club_id=club_id,
                        gender=c["gender"] if "gender" in c else "",
                        year=c["year"] if "year" in c else "",
                        chip=c["chip"] if "chip" in c else "",
                    )
                )

        if list_of_competitors:
            model.db.add_many_competitors(list_of_competitors=list_of_competitors)

    cached_result.clear_cache()

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
from ooresults.otypes.series_type import Settings
from ooresults.repo.repo import TransactionMode


def get_series_settings() -> Settings:
    with model.db.transaction():
        return model.db.get_series_settings()


def update_series_settings(settings: Settings) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.update_series_settings(settings=settings)

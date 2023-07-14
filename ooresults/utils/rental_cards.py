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


import pathlib


_rental_cards = []


def read_rental_cards(path: pathlib.Path) -> None:
    global _rental_cards

    try:
        with open(path) as f:
            _rental_cards = f.read().split()
    except FileNotFoundError:
        print(f"No rental cards read, file {path} not found")
    except Exception as e:
        print(f"Error reading file {path}:")
        print(f"  {str(e)}")


def is_rental_card(card_number: str) -> bool:
    return card_number in _rental_cards


def format_card(card_number: str) -> str:
    return f"RC ({card_number})" if card_number in _rental_cards else card_number

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
import tempfile

from ooresults.utils import rental_cards


def test_read_existing_rental_cards_file():
    rental_cards._rental_cards = []

    with tempfile.TemporaryDirectory() as hd:
        rental_cards_file = pathlib.Path(hd) / "rental_cards.txt"
        with open(rental_cards_file, "w") as f:
            f.write("123\n456\n789\n")

        rental_cards.read_rental_cards(path=rental_cards_file)
        assert rental_cards._rental_cards == ["123", "456", "789"]


def test_read_not_existing_rental_cards_file():
    rental_cards._rental_cards = []

    with tempfile.TemporaryDirectory() as hd:
        rental_cards_file = pathlib.Path(hd) / "rental_cards.txt"

        rental_cards.read_rental_cards(path=rental_cards_file)
        assert rental_cards._rental_cards == []


def test_read_empty_rental_cards_file():
    rental_cards._rental_cards = []

    with tempfile.TemporaryDirectory() as hd:
        rental_cards_file = pathlib.Path(hd) / "rental_cards.txt"
        rental_cards_file.touch()

        rental_cards.read_rental_cards(path=rental_cards_file)
        assert rental_cards_file.is_file()
        assert rental_cards._rental_cards == []


def test_read_non_utf8_rental_cards_file():
    rental_cards._rental_cards = []

    with tempfile.TemporaryDirectory() as hd:
        rental_cards_file = pathlib.Path(hd) / "rental_cards.txt"
        rental_cards_file.write_bytes(b"\xff\xff")

        rental_cards.read_rental_cards(path=rental_cards_file)
        assert rental_cards_file.is_file()
        assert rental_cards._rental_cards == []


def test_read_directory_as_rental_cards_file():
    rental_cards._rental_cards = []

    with tempfile.TemporaryDirectory() as hd:
        rental_cards_file = pathlib.Path(hd) / "rental_cards.txt"
        rental_cards_file.mkdir()

        rental_cards.read_rental_cards(path=rental_cards_file)
        assert rental_cards_file.is_dir()
        assert rental_cards._rental_cards == []


def test_is_a_rental_card():
    rental_cards._rental_cards = ["123", "456", "789"]

    assert rental_cards.is_rental_card(card_number="123") is True
    assert rental_cards.is_rental_card(card_number="456") is True
    assert rental_cards.is_rental_card(card_number="789") is True


def test_is_not_a_rental_card():
    rental_cards._rental_cards = ["123", "456", "789"]

    assert rental_cards.is_rental_card(card_number="234") is False


def test_format_a_rental_card():
    rental_cards._rental_cards = ["123", "456", "789"]

    assert rental_cards.format_card(card_number="123") == "RC (123)"
    assert rental_cards.format_card(card_number="456") == "RC (456)"
    assert rental_cards.format_card(card_number="789") == "RC (789)"


def test_format_not_a_rental_card():
    rental_cards._rental_cards = ["123", "456", "789"]

    assert rental_cards.format_card(card_number="234") == "234"

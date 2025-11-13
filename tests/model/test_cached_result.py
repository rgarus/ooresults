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


from typing import Generator
from unittest import mock

import pytest

from ooresults.model import cached_result


@pytest.fixture
def m() -> Generator[mock.Mock, None, None]:
    with mock.patch(target="ooresults.model.results.event_class_results") as obj:
        yield obj


@pytest.fixture
def fill_cache(m: mock.Mock) -> None:
    cached_result.clear_cache()

    m.return_value = "A-1"
    result = cached_result.get_cached_data(event_id=1)
    assert result == "A-1"
    assert m.call_count == 1
    m.assert_called_with(event_id=1)

    m.return_value = "A-2"
    result = cached_result.get_cached_data(event_id=2)
    assert result == "A-2"
    assert m.call_count == 2
    m.assert_called_with(event_id=2)

    m.reset_mock()


def test_if_a_cache_value_is_defined_then_the_cache_value_is_used(
    fill_cache: None, m: mock.Mock
):
    assert "A-1" == cached_result.get_cached_data(event_id=1)
    assert "A-2" == cached_result.get_cached_data(event_id=2)
    m.assert_not_called()


def test_if_the_whole_cache_is_cleared_then_all_cache_values_are_recomputed(
    fill_cache: None, m: mock.Mock
):
    cached_result.clear_cache()

    m.return_value = "B-1"
    assert "B-1" == cached_result.get_cached_data(event_id=1)
    m.return_value = "B-2"
    assert "B-2" == cached_result.get_cached_data(event_id=2)

    assert m.call_count == 2
    assert m.call_args_list == [mock.call(event_id=1), mock.call(event_id=2)]


def test_cache_can_be_cleared_for_a_special_event(fill_cache: None, m: mock.Mock):
    cached_result.clear_cache(event_id=1)

    m.return_value = "B-1"
    assert "B-1" == cached_result.get_cached_data(event_id=1)
    assert "A-2" == cached_result.get_cached_data(event_id=2)
    m.assert_called_once_with(event_id=1)


def test_at_least_max_size_events_can_be_stored_in_the_cache(m: mock.Mock):
    cached_result.clear_cache()
    max_size = cached_result.MAX_SIZE

    for i in range(max_size):
        m.return_value = i
        cached_result.get_cached_data(event_id=i)
        assert i == cached_result.get_cached_data(event_id=i)

    m.reset_mock()
    for i in range(max_size):
        m.return_value = 99
        assert i == cached_result.get_cached_data(event_id=i)

    m.assert_not_called()


def test_at_most_max_size_events_can_be_stored_in_the_cache(m: mock.Mock):
    cached_result.clear_cache()
    max_size = cached_result.MAX_SIZE

    for i in range(max_size + 1):
        m.return_value = i
        cached_result.get_cached_data(event_id=i)
        assert i == cached_result.get_cached_data(event_id=i)

    m.reset_mock()
    m.return_value = 0
    assert 0 == cached_result.get_cached_data(event_id=0)
    m.assert_called_once_with(event_id=0)


def test_least_recently_used_events_are_stored_in_the_cache(m: mock.Mock):
    cached_result.clear_cache()
    max_size = cached_result.MAX_SIZE

    for i in range(max_size):
        m.return_value = i
        cached_result.get_cached_data(event_id=i)
        assert i == cached_result.get_cached_data(event_id=i)

    cached_result.get_cached_data(event_id=0)

    for i in range(1, max_size):
        m.return_value = max_size + i
        cached_result.get_cached_data(event_id=max_size + i)
        assert max_size + i == cached_result.get_cached_data(event_id=max_size + i)

    m.reset_mock()
    m.return_value = 99
    assert 0 == cached_result.get_cached_data(event_id=0)
    m.assert_not_called()


def test_if_a_callback_is_registered_and_the_cache_is_cleared_then_the_callback_is_called():
    m1 = mock.Mock()
    m2 = mock.Mock()
    cached_result.register(callback=m1)
    cached_result.register(callback=m2)
    cached_result.clear_cache()
    m1.assert_called_once_with(None)
    m2.assert_called_once_with(None)


def test_if_a_callback_is_registered_then_the_callback_is_called_with_event_id():
    m1 = mock.Mock()
    m2 = mock.Mock()
    cached_result.register(callback=m1)
    cached_result.register(callback=m2)
    cached_result.clear_cache(event_id=1)
    m1.assert_called_once_with(1)
    m2.assert_called_once_with(1)


def test_if_a_callback_is_unregistered_then_the_callback_is_no_longer_called():
    m1 = mock.Mock()
    m2 = mock.Mock()
    cached_result.register(callback=m1)
    cached_result.register(callback=m2)
    cached_result.unregister(callback=m1)
    cached_result.clear_cache()
    m1.assert_not_called()
    m2.assert_called_once_with(None)

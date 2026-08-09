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


import time
from unittest.mock import patch

import pytest

from ooresults.websocket_server.credentials import Credentials


@pytest.fixture
def cred() -> Credentials:
    return Credentials()


def if_two_tokens_are_created_then_the_tokens_are_different(cred: Credentials) -> None:
    token_1 = cred.create_token()
    token_2 = cred.create_token()
    assert isinstance(token_1, str)
    assert isinstance(token_2, str)
    assert len(token_1) == 64
    assert len(token_2) == 64
    assert token_1 != token_2


def test_if_a_token_is_created_then_the_token_is_stored_with_creation_time(
    cred: Credentials,
) -> None:
    t1 = time.time()
    token = cred.create_token()
    t2 = time.time()
    assert token in cred.store
    assert t1 <= cred.store[token] <= t2


def test_if_a_token_not_stored_in_credentials_is_checked_then_it_is_invalid(
    cred: Credentials,
) -> None:
    assert cred.check_token("xxx") is False


def test_if_a_token_stored_in_credentials_is_checked_then_it_is_valid(
    cred: Credentials,
) -> None:
    token = cred.create_token()
    assert cred.check_token(token) is True


def test_if_a_created_token_is_checked_within_60_seconds_then_it_is_valid(
    cred: Credentials,
) -> None:
    t = time.time()
    token = cred.create_token()
    with patch("ooresults.websocket_server.credentials.time.time", lambda: t + 59):
        assert cred.check_token(token) is True


def test_if_a_created_token_is_checked_after_60_seconds_then_it_is_invalid(
    cred: Credentials,
) -> None:
    token = cred.create_token()
    t = time.time()
    with patch("ooresults.websocket_server.credentials.time.time", lambda: t + 61):
        assert cred.check_token(token) is False


def test_expired_tokens_are_removed_from_the_credential_store_if_a_new_token_is_created(
    cred: Credentials,
) -> None:
    token_1 = cred.create_token()
    token_2 = cred.create_token()
    token_3 = cred.create_token()
    t = time.time()
    with patch("ooresults.websocket_server.credentials.time.time", lambda: t + 61):
        token = cred.create_token()
        assert token in cred.store
        assert token_1 not in cred.store
        assert token_2 not in cred.store
        assert token_3 not in cred.store


def test_not_expired_tokens_are_not_removed_from_the_credential_store_if_a_new_token_is_created(
    cred: Credentials,
) -> None:
    t = time.time()
    token_1 = cred.create_token()
    token_2 = cred.create_token()
    token_3 = cred.create_token()
    with patch("ooresults.websocket_server.credentials.time.time", lambda: t + 59):
        token = cred.create_token()
        assert token in cred.store
        assert token_1 in cred.store
        assert token_2 in cred.store
        assert token_3 in cred.store

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


import asyncio
import datetime
from typing import Optional

from ooresults import model
from ooresults.model import cached_result
from ooresults.otypes.event_type import EventType
from ooresults.repo.repo import TransactionMode


def get_events() -> list[EventType]:
    with model.db.transaction():
        events = model.db.get_events()
    events.sort(key=lambda e: e.date, reverse=True)
    return events


def get_event(id: int) -> EventType:
    with model.db.transaction():
        return model.db.get_event(id=id)


def add_event(
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: list[str],
    streaming_address: Optional[str] = None,
    streaming_key: Optional[str] = None,
    streaming_enabled: Optional[bool] = None,
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        id = model.db.add_event(
            name=name,
            date=date,
            key=key,
            publish=publish,
            series=series,
            fields=fields,
            streaming_address=streaming_address,
            streaming_key=streaming_key,
            streaming_enabled=streaming_enabled,
        )
    future = asyncio.run_coroutine_threadsafe(
        coro=model.results.websocket_server.update_event(
            event=EventType(
                id=id,
                name=name,
                date=date,
                key=key,
                publish=publish,
                series=series,
                fields=fields,
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )
        ),
        loop=model.results.websocket_server.loop,
    )
    future.result()


def update_event(
    id: int,
    name: str,
    date: datetime.date,
    key: Optional[str],
    publish: bool,
    series: Optional[str],
    fields: list[str],
    streaming_address: Optional[str] = None,
    streaming_key: Optional[str] = None,
    streaming_enabled: Optional[bool] = None,
) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.update_event(
            id=id,
            name=name,
            date=date,
            key=key,
            publish=publish,
            series=series,
            fields=fields,
            streaming_address=streaming_address,
            streaming_key=streaming_key,
            streaming_enabled=streaming_enabled,
        )

    future = asyncio.run_coroutine_threadsafe(
        coro=model.results.websocket_server.update_event(
            event=EventType(
                id=id,
                name=name,
                date=date,
                key=key,
                publish=publish,
                series=series,
                fields=fields,
                streaming_address=streaming_address,
                streaming_key=streaming_key,
                streaming_enabled=streaming_enabled,
            )
        ),
        loop=model.results.websocket_server.loop,
    )
    future.result()

    cached_result.clear_cache(event_id=id)


def delete_event(id: int) -> None:
    with model.db.transaction(mode=TransactionMode.IMMEDIATE):
        model.db.delete_entries(event_id=id)
        model.db.delete_classes(event_id=id)
        model.db.delete_courses(event_id=id)
        model.db.delete_event(id)

    cached_result.clear_cache(event_id=id)

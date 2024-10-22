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
import tempfile
import threading
import json
import bz2
from typing import List

import pytest
import pytest_asyncio
import websockets

from ooresults.repo.sqlite_repo import SqliteRepo
from ooresults.model import model
from ooresults.websocket_server.streaming import Streaming
from ooresults.websocket_server.websocket_handler import WebSocketHandler
from ooresults.repo.entry_type import EntryType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.repo.result_type import ResultStatus


@pytest.fixture
def db() -> SqliteRepo:
    with tempfile.NamedTemporaryFile() as db_file:
        model.db = SqliteRepo(db=db_file.name)
        yield model.db


@pytest.fixture
def event_id(db: SqliteRepo) -> int:
    return db.add_event(
        name="Event",
        date=datetime.date(year=2020, month=1, day=1),
        key="local",
        publish=False,
        series=None,
        fields=[],
    )


class WebSocketServer(threading.Thread):
    def __init__(
        self,
        barrier: threading.Barrier,
        host: str = "0.0.0.0",
        port: int = 8081,
    ):
        super().__init__()
        self.barrier = barrier
        self.daemon = True
        self.handler = None
        self.streaming = None
        self.host = host
        self.port = port
        self.server = None
        self.loop = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=self.loop)
        self.handler = WebSocketHandler()
        self.streaming = Streaming(loop=self.loop)

        self.server = self.loop.run_until_complete(
            websockets.serve(
                ws_handler=self.handler.handler,
                host=self.host,
                port=self.port,
            ),
        )
        self.barrier.wait()
        self.loop.run_forever()

    async def close(self):
        self.server.close()
        await self.server.wait_closed()


@pytest.fixture
def websocket_server():
    barrier = threading.Barrier(parties=2)
    model.websocket_server = WebSocketServer(barrier=barrier)
    model.websocket_server.start()
    barrier.wait()
    yield model.websocket_server
    future = asyncio.run_coroutine_threadsafe(
        coro=model.websocket_server.close(),
        loop=model.websocket_server.loop,
    )
    future.result()


@pytest.mark.asyncio
async def test_no_access_if_event_not_found(
    event_id: int,
    websocket_server: WebSocketServer,
):
    async with websockets.connect(uri="ws://localhost:8081/si1") as si1_client:
        await si1_client.send("xxx,local")
        response = await si1_client.recv()
        assert response == "__no_access__"

        # websocket is closed by the server
        with pytest.raises(websockets.ConnectionClosedOK):
            await si1_client.recv()


@pytest.mark.asyncio
async def test_no_access_if_key_not_found(
    event_id: int,
    websocket_server: WebSocketServer,
):
    async with websockets.connect("ws://localhost:8081/si1") as si1_client:
        await si1_client.send(f"{event_id},xxx")
        response = await si1_client.recv()
        assert response == "__no_access__"

        # websocket is closed by the server
        with pytest.raises(websockets.ConnectionClosedOK):
            await si1_client.recv()


@pytest.mark.asyncio
async def test_reader_status_received_if_event_and_key_found(
    event_id: int,
    websocket_server: WebSocketServer,
):
    async with websockets.connect(uri="ws://localhost:8081/si1") as si1_client:
        await si1_client.send(f"{event_id},local")
        response = await si1_client.recv()
        assert json.loads(response) == {"status": "readerOffline", "data": ""}
        await si1_client.close()


@pytest.mark.asyncio
async def test_cardreader_event_key_not_found(
    event_id: int,
    websocket_server: WebSocketServer,
):
    async with websockets.connect(
        uri="ws://localhost:8081/cardreader",
        extra_headers={"X-Event-Key": "xxx"},
    ) as reader:
        # send a cardreader state message
        item = {
            "entryType": "readerDisconnected",
            "entryTime": "2021-05-18T17:24:33+02:00",
        }
        await reader.send(bz2.compress(json.dumps(item).encode()))
        response = await reader.recv()
        assert response == 'Event for key "xxx" not found'

        # websocket is closed by the server
        with pytest.raises(websockets.ConnectionClosedOK):
            await reader.recv()


@pytest.mark.asyncio
async def test_cardreader_event_key_found_and_reader_disconnected(
    event_id: int,
    websocket_server: WebSocketServer,
):
    async with websockets.connect(uri="ws://localhost:8081/si1") as si1_client:
        await si1_client.send(f"{event_id},local")
        response = await si1_client.recv()
        assert json.loads(response) == {"status": "readerOffline", "data": ""}

        async with websockets.connect(
            uri="ws://localhost:8081/cardreader",
            extra_headers={"X-Event-Key": "local"},
        ) as reader:
            # send a cardreader state message
            item = {
                "entryType": "readerDisconnected",
                "entryTime": "2021-05-18T17:24:33+02:00",
            }
            data = bz2.compress(json.dumps(item).encode())
            await reader.send(data)
            response = await reader.recv()
            assert json.loads(response) == {
                "eventId": event_id,
                "readerStatus": "readerDisconnected",
                "event": "Event",
            }

            # si1_client receives cardreader readerDisconnected message
            response = await si1_client.recv()
            assert json.loads(response) == {"status": "readerDisconnected", "data": ""}

        # si1_client receives cardreader offline message
        response = await si1_client.recv()
        assert json.loads(response) == {"status": "readerOffline", "data": ""}

        await si1_client.close()


@pytest_asyncio.fixture
async def reader(
    event_id: int,
    websocket_server: WebSocketServer,
):
    client = await websockets.connect(
        uri="ws://localhost:8081/cardreader",
        extra_headers={"X-Event-Key": "local"},
    )
    item = {
        "entryType": "readerDisconnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    data = bz2.compress(json.dumps(item).encode())
    await client.send(data)
    response = await client.recv()
    assert json.loads(response) == {
        "eventId": event_id,
        "readerStatus": "readerDisconnected",
        "event": "Event",
    }
    yield client
    await client.close()


@pytest_asyncio.fixture
async def si1_clients(
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    websocket_server: WebSocketServer,
):
    connect = websockets.connect(uri="ws://localhost:8081/si1")
    async with connect as c1, connect as c2, connect as c3, connect as c4:
        si1_clients = [c1, c2, c3, c4]
        for c in si1_clients:
            await c.send(f"{event_id},local")
        for c in si1_clients:
            response = await c.recv()
            assert json.loads(response) == {"status": "readerDisconnected", "data": ""}
        yield si1_clients
        for c in si1_clients:
            await c.close()


@pytest.mark.asyncio
async def test_cardreader_reader_connected(
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    si1_clients: List[websockets.WebSocketClientProtocol],
    websocket_server: WebSocketServer,
):
    item = {
        "entryType": "readerConnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    data = bz2.compress(json.dumps(item).encode())
    await reader.send(data)
    response = await reader.recv()
    assert json.loads(response) == {
        "eventId": event_id,
        "readerStatus": "readerConnected",
        "event": "Event",
    }

    # new state is sent to all clients
    for c in si1_clients:
        response = await c.recv()
        assert json.loads(response) == {"status": "readerConnected", "data": ""}


@pytest.mark.asyncio
async def test_cardreader_reader_disconnected(
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    si1_clients: List[websockets.WebSocketClientProtocol],
    websocket_server: WebSocketServer,
):
    item = {
        "entryType": "readerDisconnected",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    data = bz2.compress(json.dumps(item).encode())
    await reader.send(data)
    response = await reader.recv()
    assert json.loads(response) == {
        "eventId": event_id,
        "readerStatus": "readerDisconnected",
        "event": "Event",
    }

    # new state is sent to all clients
    for c in si1_clients:
        response = await c.recv()
        assert json.loads(response) == {"status": "readerDisconnected", "data": ""}


@pytest.mark.asyncio
async def test_cardreader_card_inserted(
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    si1_clients: List[websockets.WebSocketClientProtocol],
    websocket_server: WebSocketServer,
):
    item = {
        "entryType": "cardInserted",
        "entryTime": "2021-05-18T17:24:33+02:00",
        "controlCard": "84752",
    }
    data = bz2.compress(json.dumps(item).encode())
    await reader.send(data)
    response = await reader.recv()
    assert json.loads(response) == {
        "eventId": event_id,
        "controlCard": "84752",
        "readerStatus": "cardInserted",
        "event": "Event",
    }

    # new state is sent to all clients
    for c in si1_clients:
        response = await c.recv()
        assert json.loads(response) == {"status": "cardInserted", "data": "84752"}


@pytest.mark.asyncio
async def test_cardreader_card_removed(
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    si1_clients: List[websockets.WebSocketClientProtocol],
    websocket_server: WebSocketServer,
):
    item = {
        "entryType": "cardRemoved",
        "entryTime": "2021-05-18T17:24:33+02:00",
    }
    data = bz2.compress(json.dumps(item).encode())
    await reader.send(data)
    response = await reader.recv()
    assert json.loads(response) == {
        "eventId": event_id,
        "readerStatus": "cardRemoved",
        "event": "Event",
    }

    # new state is sent to all clients
    for c in si1_clients:
        response = await c.recv()
        assert json.loads(response) == {"status": "cardRemoved", "data": ""}


@pytest.mark.asyncio
async def test_cardreader_card_read(
    db,
    event_id: int,
    reader: websockets.WebSocketClientProtocol,
    si1_clients: List[websockets.WebSocketClientProtocol],
    websocket_server: WebSocketServer,
):
    item = {
        "entryType": "cardRead",
        "entryTime": "2021-05-18T17:24:33+02:00",
        "cardType": "SI10",
        "controlCard": "8084753",
        "startTime": "2021-05-18T16:31:19+02:00",
        "finishTime": "2021-05-18T16:31:50+02:00",
        "checkTime": "2021-05-18T16:31:18+02:00",
        "punches": [
            {"controlCode": "141", "punchTime": "2021-05-18T16:31:25+02:00"},
            {"controlCode": "143", "punchTime": "2021-05-18T16:31:31+02:00"},
        ],
    }
    data = bz2.compress(json.dumps(item).encode())
    await reader.send(data)
    response = await reader.recv()
    assert json.loads(response) == {
        "entryTime": "17:24:33",
        "eventId": 1,
        "controlCard": "8084753",
        "firstName": None,
        "lastName": None,
        "club": None,
        "class": None,
        "status": "FINISHED",
        "time": None,
        "error": "Control card unknown",
        "readerStatus": "cardRead",
        "event": "Event",
    }

    # new state is sent to all clients
    for c in si1_clients:
        response = await c.recv()
        assert json.loads(response)["status"] == "cardRead"

    # result is stored in database
    ch = datetime.datetime.fromisoformat("2021-05-18T16:31:18+02:00")
    s1 = datetime.datetime.fromisoformat("2021-05-18T16:31:19+02:00")
    f1 = datetime.datetime.fromisoformat("2021-05-18T16:31:50+02:00")
    c1 = datetime.datetime.fromisoformat("2021-05-18T16:31:25+02:00")
    c2 = datetime.datetime.fromisoformat("2021-05-18T16:31:31+02:00")

    data = db.get_entries(event_id=event_id)
    assert data == [
        EntryType(
            id=data[0].id,
            event_id=event_id,
            competitor_id=None,
            first_name=None,
            last_name=None,
            chip="8084753",
            result=PersonRaceResult(
                status=ResultStatus.FINISHED,
                start_time=s1,
                finish_time=f1,
                punched_check_time=ch,
                punched_start_time=s1,
                punched_finish_time=f1,
                si_punched_start_time=s1,
                si_punched_finish_time=f1,
                time=31,
                split_times=[
                    SplitTime(
                        control_code="141",
                        punch_time=c1,
                        si_punch_time=c1,
                        time=6,
                        status=SpStatus.ADDITIONAL,
                    ),
                    SplitTime(
                        control_code="143",
                        punch_time=c2,
                        si_punch_time=c2,
                        time=12,
                        status=SpStatus.ADDITIONAL,
                    ),
                ],
            ),
        ),
    ]

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
from typing import Any
from unittest import mock

import pytest
import pytest_asyncio
import websockets.exceptions
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect
from websockets.protocol import State

import ooresults.model
from ooresults.otypes.class_params import ClassParams
from ooresults.otypes.class_type import ClassInfoType
from ooresults.otypes.event_type import EventType
from ooresults.websocket_server import streaming
from ooresults.websocket_server import streaming_status
from ooresults.websocket_server.streaming_status import Status


@pytest.fixture
def event() -> EventType:
    return EventType(
        id=3,
        name="ABC",
        date=datetime.date(year=2020, month=1, day=1),
        key=None,
        publish=False,
        series=None,
        fields=[],
        streaming_address="a",
        streaming_key="a",
        streaming_enabled=False,
    )


@pytest.fixture
def class_info() -> ClassInfoType:
    return ClassInfoType(
        id=5,
        name="Elite",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


class SleepAsyncMock(mock.AsyncMock):
    def __init__(self):
        super().__init__()
        self.side_effect = self._sleep
        self.event_sync = asyncio.Event()
        self.event_continue = asyncio.Event()
        self.first = True

    async def sync(self):
        if self.first:
            self.first = False
        else:
            self.event_continue.set()
        await self.event_sync.wait()
        self.event_sync.clear()

    async def _sleep(self, delay: float) -> None:
        self.event_sync.set()
        await self.event_continue.wait()
        self.event_continue.clear()


@pytest_asyncio.fixture
async def mock_sleep():
    with mock.patch(
        target="asyncio.sleep",
        spec=asyncio.sleep,
        spec_set=True,
        new=SleepAsyncMock(),
    ) as m:
        yield m


@pytest_asyncio.fixture
async def mock_connect():
    with mock.patch(
        target="ooresults.websocket_server.streaming.connect",
        spec=connect,
        spec_set=True,
        new=mock.AsyncMock(),
    ) as m:
        yield m


@pytest.fixture
def mock_get_events():
    with mock.patch(
        target="ooresults.model.events.get_events",
        spec=ooresults.model.events.get_events,
        spec_set=True,
        new=mock.Mock(),
    ) as m:
        yield m


@pytest.fixture
def mock_event_class_results():
    with mock.patch(
        target="ooresults.model.results.event_class_results",
        spec=ooresults.model.results.event_class_results,
        spec_set=True,
        new=mock.Mock(),
    ) as m:
        yield m


@pytest.fixture
def parent(
    mock_get_events: mock.Mock,
    mock_event_class_results: mock.Mock,
    mock_connect: mock.AsyncMock,
    mock_sleep: SleepAsyncMock,
):
    parent = mock.MagicMock()
    parent.mock_get_events = mock_get_events
    parent.mock_event_class_results = mock_event_class_results
    parent.mock_connect = mock_connect
    parent.mock_sleep = mock_sleep
    return parent


class C:
    def __init__(self, name: str, args=None, kwargs=None, value: Any = None):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.value = value


def check_calls(parent: mock.MagicMock, calls: list[C]):
    for i, c in enumerate(parent.mock_calls):
        name, args, kwargs = c
        print(c, name, args, kwargs)
        assert name == calls[i].name, i
        if calls[i].args is not None:
            assert args == calls[i].args, i
        if calls[i].kwargs is not None:
            assert kwargs == calls[i].kwargs, i

    c = [v.name for v in calls if v.name == "mock_get_events"]
    assert parent.mock_get_events.call_count == len(c)
    c = [v.name for v in calls if v.name == "mock_connect"]
    assert parent.mock_connect.await_count == len(c)
    c = [v.name for v in calls if v.name == "mock_event_class_results"]
    assert parent.mock_event_class_results.call_count == len(c)
    c = [v.name for v in calls if v.name == "mock_ws.send"]
    # assert parent.mock_connect.return_value.send.await_count == len(c)
    c = [v.name for v in calls if v.name == "mock_ws.recv"]
    # assert parent.mock_connect.return_value.recv.await_count == len(c)
    c = [v.name for v in calls if v.name == "mock_sleep"]
    assert parent.mock_sleep.await_count == len(c)


def value_calls(parent: mock.MagicMock, calls: list[C]):
    for i, c in enumerate(calls):
        if c.name == "mock_connect":
            if c.value == ClientConnection:
                parent.mock_connect.side_effect = None
                parent.mock_connect.return_value = mock.create_autospec(
                    spec=ClientConnection, spec_set=True
                )
                parent.attach_mock(parent.mock_connect.return_value, "mock_ws")
                parent.mock_connect.return_value.state = State.OPEN
            else:
                parent.mock_connect.side_effect = c.value

    c = [v.value for v in calls if v.name == "mock_get_events"]
    parent.mock_get_events.side_effect = c
    c = [v.value for v in calls if v.name == "mock_event_class_results"]
    parent.mock_event_class_results.side_effect = c
    c = [v.value for v in calls if v.name == "mock_ws.send"]
    parent.mock_connect.return_value.send.side_effect = c
    c = [v.value for v in calls if v.name == "mock_ws.recv"]
    parent.mock_connect.return_value.recv.side_effect = c


@pytest.mark.asyncio
async def test_if_streaming_is_disabled_then_connect_is_not_called_after_software_start(
    event: EventType,
    mock_get_events: mock.Mock,
    mock_connect: mock.AsyncMock,
):
    loop = asyncio.get_running_loop()

    mock_get_events.return_value = [event]
    mock_connect.return_value = mock.create_autospec(
        spec=ClientConnection, spec_set=True
    )

    s = streaming.Streaming(loop=loop)
    await asyncio.sleep(0)
    mock_connect.assert_not_awaited()
    assert streaming_status.status.get(id=event.id) is None
    assert len(s.events) == 0
    assert len(s.tasks) == 0


@pytest.mark.asyncio
async def test_if_streaming_is_enabled_then_connect_is_called_until_connected(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> OSError()
    # sleep(20)
    # connect -> OSError()
    # sleep(20)
    # connect -> ClientConnection()
    # event_class_results -> event(3), []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> OSError()
        C(name="mock_connect", value=OSError()),
        # sleep(20)
        C(name="mock_sleep", kwargs={"delay": 20}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.NOT_CONNECTED

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> OSError()
        C(name="mock_connect", value=OSError()),
        # sleep(20)
        C(name="mock_sleep", kwargs={"delay": 20}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.NOT_CONNECTED

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_answer_is_event_not_found_then_reconnect_after_45_sec(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "eventNotFound"}'
    # sleep(45)
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "eventNotFound"}'
    # sleep(45)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "eventNotFound"}'
        C(name="mock_ws.recv", value='{"result": "eventNotFound"}'),
        # sleep(45)
        C(name="mock_sleep", kwargs={"delay": 45}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.EVENT_NOT_FOUND

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "eventNotFound"}'
        C(name="mock_ws.recv", value='{"result": "eventNotFound"}'),
        # sleep(45)
        C(name="mock_sleep", kwargs={"delay": 45}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.EVENT_NOT_FOUND

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_no_answer_then_reconnect_after_45_sec(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> TimeoutError()'
    # sleep(15)
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> TimeoutError()'
    # sleep(15)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> TimeoutError()'
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(15)
        C(name="mock_sleep", kwargs={"delay": 15}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.PROTOCOL_ERROR

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> TimeoutError}'
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(15)
        C(name="mock_sleep", kwargs={"delay": 15}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.PROTOCOL_ERROR

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_unexpected_answer_then_reconnect_after_45_sec(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '???'
    # sleep(45)
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '???'
    # sleep(45)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '???'
        C(name="mock_ws.recv", value="???"),
        # sleep(45)
        C(name="mock_sleep", kwargs={"delay": 45}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.PROTOCOL_ERROR

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '???'
        C(name="mock_ws.recv", value="???"),
        # sleep(45)
        C(name="mock_sleep", kwargs={"delay": 45}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.PROTOCOL_ERROR

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_answer_is_error_then_repeat_sending_actual_result_after_30_sec(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "error"}'
    # recv -> Timeout
    # sleep(0)
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "error"}'
    # recv -> Timeout()
    # sleep(0)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "error"}'
        C(name="mock_ws.recv", value='{"result": "error"}'),
        # recv -> Timeout
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.ERROR

    check_calls(parent=parent, calls=calls)
    c1 = [
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "error"}'
        C(name="mock_ws.recv", value='{"result": "error"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1

    value_calls(parent=parent, calls=c1)
    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.ERROR

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_after_connect_an_unknown_exception_is_raised_new_state_is_internal_error(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> Exception()
    # sleep(30)
    # connect -> ClientConnection()
    # event_class_results -> Exception()
    # sleep(30)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=Exception()),
        # sleep(30)
        C(name="mock_sleep", kwargs={"delay": 30}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.INTERNAL_ERROR

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=Exception()),
        # sleep(30)
        C(name="mock_sleep", kwargs={"delay": 30}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.INTERNAL_ERROR

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_answer_is_ok_then_repeat_sending_different_results_every_30_sec(
    event: EventType,
    class_info: ClassInfoType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    c1 = [
        # event_class_results(3) -> event, [(class_info, [])]
        C(
            name="mock_event_class_results",
            kwargs={"event_id": 3},
            value=(event, [(class_info, [])]),
        ),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0))
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_answer_is_ok_then_do_not_send_the_same_result_again(
    event: EventType,
    class_info: ClassInfoType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)
    # event_class_results -> event, []
    # recv -> Timeout()
    # sleep(0)
    # event_class_results -> event, [(class_info, [])]
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    c1 = [
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    c1 = [
        # event_class_results(3) -> event, [(class_info, [])]
        C(
            name="mock_event_class_results",
            kwargs={"event_id": 3},
            value=(event, [(class_info, [])]),
        ),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_answer_is_ok_and_connection_closed_then_reconnect_after_30_sec(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> ConnectionClosed()
    # sleep(30)
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(30)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> ConnectionClosed
        C(
            name="mock_ws.recv",
            value=websockets.exceptions.ConnectionClosed(rcvd=None, sent=None),
        ),
        # sleep(30)
        C(name="mock_sleep", kwargs={"delay": 30}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.NOT_CONNECTED

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_stream_parameters_are_changed_then_reconnect(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)
    #
    # await s.update_event(event=event)
    #
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    event.streaming_key = "b"
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # update event
    parent.mock_sleep.first = True
    await s.update_event(event=event)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)


@pytest.mark.asyncio
async def test_if_stream_is_disabled_then_results_are_no_longer_send(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = True

    # call order of mocked objects in Streaming.stream()
    #
    # get_events -> [event]
    # connect -> ClientConnection()
    # event_class_results -> event, []
    # send
    # recv -> '{"result": "ok"}'
    # recv -> Timeout()
    # sleep(0)
    #
    # await s.update_event(event=event)

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results(3) -> event, []
        C(name="mock_event_class_results", kwargs={"event_id": 3}, value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    assert len(s.events) == 1
    assert len(s.tasks) == 1
    streaming_task = s.tasks[event.id]

    # update event
    event.streaming_enabled = False
    await s.update_event(event)

    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(streaming_task, timeout=0.1)
    # assertions
    assert streaming_status.status.get(id=event.id) is None

    assert len(s.events) == 0
    assert len(s.tasks) == 0

    check_calls(parent=parent, calls=calls)


@pytest.mark.asyncio
async def test_if_stream_is_disabled_then_connect_is_not_called(
    event: EventType,
    parent: mock.MagicMock,
):
    loop = asyncio.get_running_loop()
    event.streaming_enabled = False

    calls = [
        # get_events -> [event]
        C(name="mock_get_events", value=[event]),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=loop)

    assert len(s.events) == 0
    assert len(s.tasks) == 0

    # update event
    await s.update_event(event=event)

    assert streaming_status.status.get(id=event.id) is None

    check_calls(parent=parent, calls=calls)
    assert len(s.events) == 0
    assert len(s.tasks) == 0


@pytest.mark.asyncio
async def test_if_stream_is_enabled_then_connect_to_server(
    event: EventType,
    parent: mock.MagicMock,
):
    calls = [
        # get_events -> []
        C(name="mock_get_events", value=[event]),
    ]
    value_calls(parent=parent, calls=calls)
    s = streaming.Streaming(loop=asyncio.get_running_loop())

    assert len(s.events) == 0
    assert len(s.tasks) == 0

    check_calls(parent=parent, calls=calls)
    c1 = [
        # connect -> ClientConnection()
        C(name="mock_connect", value=ClientConnection),
        # event_class_results -> event, []
        C(name="mock_event_class_results", value=(event, [])),
        # send
        C(name="mock_ws.send"),
        # recv -> '{"result": "ok"}'
        C(name="mock_ws.recv", value='{"result": "ok"}'),
        # recv -> Timeout()
        C(name="mock_ws.recv", value=asyncio.TimeoutError()),
        # sleep(0)
        C(name="mock_sleep", kwargs={"delay": 0}),
    ]
    calls += c1
    value_calls(parent=parent, calls=c1)

    # update event
    event.streaming_enabled = True
    await s.update_event(event=event)

    assert len(s.events) == 1
    assert len(s.tasks) == 1

    # synchronize
    await parent.mock_sleep.sync()
    # assertions
    assert streaming_status.status.get(id=event.id) == Status.OK

    check_calls(parent=parent, calls=calls)
    # stop streaming
    event.streaming_enabled = False
    await s.update_event(event)

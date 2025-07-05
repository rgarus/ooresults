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


import dataclasses
import threading
import typing
from collections import OrderedDict
from typing import Optional

from ooresults import model
from ooresults.utils import render


@dataclasses.dataclass
class Data:
    content: Optional[str] = None
    lock: threading.Lock = threading.Lock()
    valid: bool = True


maxsize = 4
lock = threading.Lock()
caches: typing.OrderedDict[int, Data] = OrderedDict()


def get_cached_data(event_id: int):
    with lock:
        cached_data = caches.get(event_id, None)

        if cached_data is None:
            cached_data = Data()
            caches[event_id] = cached_data
        elif not cached_data.valid:
            cached_data.valid = True
            cached_data.content = None
        elif cached_data.content is not None:
            caches.move_to_end(key=event_id)
            return cached_data.content

        event_lock = cached_data.lock

    with event_lock:
        cached_data = caches.get(event_id, None)

        if not (cached_data and cached_data.content is not None and cached_data.valid):
            event, class_results = model.results.event_class_results(event_id=event_id)
            content = render.results_table(event=event, class_results=class_results)

            with lock:
                cached_data = caches.get(event_id, None)
                if cached_data:
                    cached_data.content = content
                    caches.move_to_end(key=event_id)
                    if len(caches) > maxsize:
                        caches.popitem(last=False)

        return cached_data.content


def clear_cache(event_id: Optional[int] = None, entry_id: Optional[int] = None) -> None:
    with lock:
        if event_id is None:
            for d in caches.values():
                d.valid = False

        elif event_id in caches:
            caches[event_id].valid = False

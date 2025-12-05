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
import logging
import threading
import time
import typing
from collections import OrderedDict
from typing import Optional

import bottle

from ooresults import model
from ooresults.model import cached_result
from ooresults.utils import render


"""
Handler for the root routes.

/
"""


@dataclasses.dataclass
class Data:
    content: Optional[str] = None
    valid: bool = True


MAX_SIZE = 4

lock = threading.Lock()
cache: typing.OrderedDict[int, Data] = OrderedDict()


def callback(event_id: Optional[int]) -> None:
    with lock:
        if event_id is None:
            for d in cache.values():
                d.valid = False
        elif event_id in cache:
            cache[event_id].valid = False


@bottle.get("/")
def get_root():
    t1 = time.time()

    events = model.events.get_events()
    for event in events:
        if event.publish:

            with lock:
                cached_data = cache.get(event.id, None)

                if cached_data is None:
                    cached_data = Data()
                    cache[event.id] = cached_data
                elif not cached_data.valid:
                    cached_data.valid = True
                    cached_data.content = None
                elif cached_data.content is not None:
                    content = cached_data.content
                    cache.move_to_end(key=event.id)
                    break

            event, class_results = cached_result.get_cached_data(event_id=event.id)
            results_table = render.results_table(
                event=event, class_results=class_results
            )
            content = render.root(results_table=results_table)

            with lock:
                cached_data = cache.get(event.id, None)
                if not (
                    cached_data
                    and cached_data.content is not None
                    and cached_data.valid
                ):
                    cached_data.content = content
                    cache.move_to_end(key=event.id)
                if len(cache) > MAX_SIZE:
                    cache.popitem(last=False)
            break
    else:
        content = render.root(results_table=None)

    t2 = time.time()
    logging.info(
        f"Rendering result, {bottle.request.environ['REMOTE_ADDR']}, {t2 - t1:.4f}"
    )
    return content


cached_result.register(callback=callback)

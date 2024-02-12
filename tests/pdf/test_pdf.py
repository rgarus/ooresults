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


from typing import Optional

import pytest

from ooresults.pdf.pdf import PDF
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.class_type import ClassParams


testdata = [
    (None, None, None, ""),
    (2300, None, None, "2300 m"),
    (None, 120, None, "120 Hm"),
    (2300, 120, None, "2300 m - 120 Hm"),
    (None, None, 0, ""),
    (None, None, 1, "1 Posten"),
    (None, None, 24, "24 Posten"),
    (5000, None, 1, "5000 m - 1 Posten"),
    (None, 50, 9, "50 Hm - 9 Posten"),
    (4070, 60, 17, "4070 m - 60 Hm - 17 Posten"),
]


@pytest.mark.parametrize("length,climb,number_of_controls,result", testdata)
def test_course_data(
    length: Optional[int],
    climb: Optional[int],
    number_of_controls: Optional[int],
    result: str,
):
    class_info = ClassInfoType(
        id=1,
        name="cl",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=length,
        course_climb=climb,
        number_of_controls=number_of_controls,
        params=ClassParams(),
    )
    pdf = PDF(name="abc")
    assert pdf.course_data(class_info=class_info) == result

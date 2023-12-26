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


from typing import List
from typing import Tuple
from typing import Any
from typing import Optional

from ooresults.pdf.pdf import PDF
from ooresults.repo.event_type import EventType
from ooresults.repo.series_type import Settings
from ooresults.repo.series_type import PersonSeriesResult


def create_pdf(
    settings: Settings,
    events: List[EventType],
    results: List[Tuple[str, List[PersonSeriesResult]]],
    landscape: bool = False,
) -> bytes:
    W_SPACE = 3
    W_RANK = 9
    W_NAME = 40
    W_YEAR = 10
    W_SUM = 15 + 2
    W_POINTS = 15 + 2

    # to set the results right aligned with the right margin (minus W_RANK) we extend the club space
    W_CLUB = 297 - 20 if landscape else 210 - 20
    W_CLUB -= (W_RANK + W_SPACE + W_NAME + W_SPACE + W_YEAR + W_SPACE) + W_RANK
    W_CLUB -= W_SUM + len(events) * W_POINTS

    # Instantiation of inherited class
    pdf = PDF(name=settings.name, landscape=landscape)
    pdf.set_margin(margin=10)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    def cell(w: int, h: Optional[int] = None, txt: str = "", align: str = "L") -> None:
        if w > 0:
            while pdf.get_string_width(txt) > w:
                txt = txt[:-1]
            pdf.cell(w=w, h=h, txt=txt, align=align)

    for i, class_results in enumerate(results):
        class_name, series_results = class_results
        if i > 0:
            # insert a page break if there is not enough space left on the
            # page for the class header, the table header and two table rows
            if pdf.will_page_break(height=30):
                pdf.add_page()
            else:
                pdf.ln()
                pdf.ln()

        pdf.set_font(family="Carlito", style="B", size=12)
        pdf.cell(txt=class_name)
        pdf.ln()
        pdf.ln()
        pdf.set_font(family="Carlito", style="I", size=10)
        cell(w=W_RANK, h=None, txt="Pl", align="R")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_NAME, h=None, txt="Name", align="L")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_YEAR, h=None, txt="Jg", align="R")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_CLUB, h=None, txt="Verein", align="L")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_SUM, h=None, txt="Gesamt", align="R")
        for e in events:
            cell(w=W_POINTS, h=None, txt=e.series, align="R")
        pdf.ln()
        pdf.ln()

        for ser_result in series_results:

            def get(value: Any) -> Any:
                return value if value is not None else ""

            if ser_result.races != {}:
                print(class_name, ser_result)
                pdf.set_font(family="Carlito", size=10)
                cell(
                    w=W_RANK,
                    h=None,
                    txt=str(ser_result.rank) if ser_result.rank is not None else "-",
                    align="R",
                )
                cell(w=W_SPACE, h=None, txt="")
                cell(
                    w=W_NAME,
                    h=None,
                    txt=get(ser_result.last_name) + " " + get(ser_result.first_name),
                    align="L",
                )
                cell(w=W_SPACE, h=None, txt="")
                cell(w=W_YEAR, h=None, txt=str(get(ser_result.year)), align="R")
                cell(w=W_SPACE, h=None, txt="")
                cell(w=W_CLUB, h=None, txt=get(ser_result.club_name), align="L")
                cell(w=W_SPACE, h=None, txt="")
                pdf.set_font(style="B")
                cell(
                    w=W_SUM,
                    h=None,
                    txt=str(ser_result.total_points),
                    align="R",
                )
                pdf.set_font()
                for i in range(len(events)):
                    if i in ser_result.races:
                        if ser_result.races[i].bonus:
                            cell(
                                w=W_POINTS,
                                h=None,
                                txt="(" + str(ser_result.races[i].points) + ")",
                                align="R",
                            )
                        else:
                            cell(
                                w=W_POINTS,
                                h=None,
                                txt=str(ser_result.races[i].points),
                                align="R",
                            )
                    else:
                        cell(
                            w=W_POINTS,
                            h=None,
                            txt="-----",
                            align="R",
                        )
                pdf.ln()

    return bytes(pdf.output())

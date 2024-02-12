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
from typing import Optional
from typing import Union

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import ResultStatus
from ooresults.pdf.pdf import PDF
from ooresults.utils import globals


def create_pdf(
    event: EventType,
    results: List[Tuple[ClassInfoType, List[RankedEntryType]]],
    include_dns: bool = False,
    landscape: bool = True,
) -> bytes:
    W_SPACE = 4
    W_RANK = 9
    W_NAME = 60
    W_YEAR = 10
    W_CLUB = 60
    W_RUNTIME = 15
    W_VALUE = 20
    W_TOTAL = 24

    if landscape:
        W_CLUB = 175
    else:
        W_CLUB = 175 - 87

    # Instantiation of inherited class
    pdf = PDF(name=event.name, landscape=landscape)
    pdf.set_margin(margin=10)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    def cell(w: int, h: Optional[int] = None, txt: str = "", align: str = "L") -> None:
        while pdf.get_string_width(txt) > w:
            txt = txt[:-1]
        pdf.cell(w=w, h=h, txt=txt, align=align)

    def print_time(width: int, time: int, status: ResultStatus) -> None:
        txt = ""
        if status == ResultStatus.OK:
            txt = globals.minutes_seconds(time)
        cell(w=width, h=None, txt=txt, align="R")

    def print_time_or_status(width: int, time: int, status: ResultStatus) -> None:
        txt = pdf.MAP_STATUS[status]
        if status == ResultStatus.OK:
            txt = globals.minutes_seconds(time)
        cell(w=width, h=None, txt=txt, align="R")

    def print_points(width: int, points: Optional[float], status: ResultStatus) -> None:
        txt = ""
        if points is not None and status == ResultStatus.OK:
            txt = "{:.2f}".format(points)
        cell(w=width, h=None, txt=txt, align="R")

    def print_points_or_status(
        width: int, points: Optional[float], status: ResultStatus
    ) -> None:
        txt = pdf.MAP_STATUS[status]
        if points is not None and status == ResultStatus.OK:
            txt = "{:.2f}".format(points)
        cell(w=width, h=None, txt=txt, align="R")

    for i, class_results in enumerate(results):
        class_, ranked_results = class_results

        if not include_dns:
            # filter results - use only started entries
            ranked_results = [
                r
                for r in ranked_results
                if r.entry.result.status
                not in (
                    ResultStatus.INACTIVE,
                    ResultStatus.DID_NOT_START,
                )
            ]

        # do not print classes without entries
        if not ranked_results:
            continue

        if i > 0:
            # insert a page break if there is not enough space left on the
            # page for the class header, the table header and two table rows
            if pdf.will_page_break(height=33):
                pdf.add_page()
            else:
                pdf.ln()
                pdf.ln()

        width = 0
        if class_.params.otype == "score":
            width += W_RUNTIME
            width += W_VALUE
            width += W_VALUE
            if class_.params.apply_handicap_rule:
                width += W_VALUE
            width += W_TOTAL
        else:
            if (
                class_.params.penalty_controls is not None
                or class_.params.penalty_overtime is not None
                or class_.params.apply_handicap_rule
            ):
                width += W_RUNTIME
            if class_.params.penalty_controls is not None:
                width += W_VALUE
            if class_.params.penalty_overtime is not None:
                width += W_VALUE
            if class_.params.apply_handicap_rule:
                width += W_VALUE
            width += W_TOTAL

        pdf.set_font(family="Carlito", style="B", size=12)
        pdf.cell(txt=f"{class_.name}   ({len(ranked_results)})")

        # print possible voided legs
        if ranked_results and ranked_results[0].entry.result is not None:
            voided_legs = ranked_results[0].entry.result.voided_legs()
            if voided_legs:
                pdf.cell(txt=f'(Voided legs: {", ".join(voided_legs)})')

        # course data
        course_data = pdf.course_data(class_)
        if course_data:
            pdf.set_x(x=max(pdf.get_x() + 15, 100))
            pdf.cell(txt=course_data)

        pdf.ln()
        pdf.ln()
        pdf.set_font(family="Carlito", style="I", size=10)
        cell(w=W_RANK, h=None, txt="Pl", align="R")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_NAME, h=None, txt="Name", align="L")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_YEAR, h=None, txt="Jg", align="R")
        cell(w=W_SPACE, h=None, txt="")
        cell(w=W_CLUB - width, h=None, txt="Verein", align="L")
        cell(w=W_SPACE, h=None, txt="")
        if class_.params.otype == "score":
            if class_.params.apply_handicap_rule:
                cell(w=W_VALUE, h=None, txt="Faktor", align="R")
            cell(w=W_RUNTIME, h=None, txt="Laufzeit", align="R")
            cell(w=W_VALUE, h=None, txt="Sc-Posten", align="R")
            cell(w=W_VALUE, h=None, txt="Sc-Zeit", align="R")
            cell(w=W_TOTAL, h=None, txt="Score", align="R")
        else:
            if (
                class_.params.penalty_controls is not None
                or class_.params.penalty_overtime is not None
                or class_.params.apply_handicap_rule
            ):
                cell(w=W_RUNTIME, h=None, txt="Laufzeit", align="R")
            if class_.params.penalty_controls is not None:
                cell(w=W_VALUE, h=None, txt="Str-Posten", align="R")
            if class_.params.penalty_overtime is not None:
                cell(w=W_VALUE, h=None, txt="Str-Zeit", align="R")
            if class_.params.apply_handicap_rule:
                cell(w=W_VALUE, h=None, txt="Faktor", align="R")
            cell(w=W_TOTAL, h=None, txt="Zeit", align="R")
        pdf.ln()
        pdf.ln()

        ranked = False
        for ranked_result in ranked_results:
            entry = ranked_result.entry
            result = entry.result

            def f(value: Union[Optional[int], Optional[str]]) -> str:
                return str(value) if value is not None else ""

            pdf.set_font(family="Carlito", size=12)
            if ranked_result.rank is not None:
                ranked = True
            elif ranked:
                ranked = False
                pdf.ln()
            cell(
                w=W_RANK,
                h=None,
                txt=f(ranked_result.rank) if not entry.not_competing else "AK",
                align="R",
            )
            cell(w=W_SPACE, h=None, txt="")
            cell(
                w=W_NAME,
                h=None,
                txt=f(entry.last_name) + " " + f(entry.first_name),
                align="L",
            )
            cell(w=W_SPACE, h=None, txt="")
            cell(w=W_YEAR, h=None, txt=f(entry.year), align="R")
            cell(w=W_SPACE, h=None, txt="")
            cell(w=W_CLUB - width, h=None, txt=f(entry.club_name), align="L")
            cell(w=W_SPACE, h=None, txt="")
            if class_.params.otype == "score":
                if class_.params.apply_handicap_rule:
                    if result.status == ResultStatus.OK:
                        cell(
                            w=W_VALUE,
                            h=None,
                            txt="{:1.4f}".format(result.extensions.get("factor", 1)),
                            align="R",
                        )
                    else:
                        cell(w=W_VALUE, h=None, txt="")
                print_time(
                    width=W_RUNTIME,
                    time=result.time,
                    status=result.status,
                )
                print_points(
                    width=W_VALUE,
                    points=result.extensions.get("score_controls", None),
                    status=result.status,
                )
                print_points(
                    width=W_VALUE,
                    points=result.extensions.get("score_overtime", None),
                    status=result.status,
                )
                print_points_or_status(
                    width=W_TOTAL,
                    points=result.extensions.get("score", None),
                    status=result.status,
                )
            else:
                if (
                    class_.params.penalty_controls is not None
                    or class_.params.penalty_overtime is not None
                    or class_.params.apply_handicap_rule
                ):
                    print_time(
                        width=W_RUNTIME,
                        time=result.extensions.get("running_time", None),
                        status=result.status,
                    )
                if class_.params.penalty_controls is not None:
                    print_time(
                        width=W_VALUE,
                        time=result.extensions.get("penalties_controls", None),
                        status=result.status,
                    )
                if class_.params.penalty_overtime is not None:
                    print_time(
                        width=W_VALUE,
                        time=result.extensions.get("penalties_overtime", None),
                        status=result.status,
                    )
                if class_.params.apply_handicap_rule:
                    if result.status == ResultStatus.OK:
                        cell(
                            w=W_VALUE,
                            h=None,
                            txt="{:1.4f}".format(result.extensions.get("factor", 1)),
                            align="R",
                        )
                    else:
                        cell(w=W_VALUE, h=None, txt="")
                print_time_or_status(
                    width=W_TOTAL,
                    time=result.time,
                    status=result.status,
                )
            pdf.ln()

    return bytes(pdf.output())

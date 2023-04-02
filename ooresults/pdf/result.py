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


from typing import Dict
from typing import Optional
from typing import Any

from ooresults.repo.result_type import ResultStatus
from ooresults.pdf.pdf import PDF
from ooresults.utils import globals


def create_pdf(
    event: Dict, results: Dict, include_dns: bool = False, landscape: bool = True
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

        # number of entries
        nr_entries = 0
        for result in ranked_results:
            if include_dns or result["result"].status not in (
                ResultStatus.INACTIVE,
                ResultStatus.DID_NOT_START,
            ):
                nr_entries += 1

        pdf.set_font(family="Carlito", style="B", size=12)
        pdf.cell(txt=f"{class_.name}   ({nr_entries})")

        # print possible voided legs
        if ranked_results and ranked_results[0]["result"] is not None:
            voided_legs = ranked_results[0]["result"].voided_legs()
            if voided_legs:
                pdf.cell(txt=f'(Voided legs: {", ".join(voided_legs)})')

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
        for result in ranked_results:

            def get(d: Dict, key: str) -> Any:
                s = d.get(key, "")
                return s if s is not None else ""

            if include_dns or result["result"].status not in (
                ResultStatus.INACTIVE,
                ResultStatus.DID_NOT_START,
            ):
                pdf.set_font(family="Carlito", size=12)
                if result.rank is not None:
                    ranked = True
                elif ranked:
                    ranked = False
                    pdf.ln()
                cell(
                    w=W_RANK,
                    h=None,
                    txt=str(get(result, "rank"))
                    if not get(result, "not_competing")
                    else "AK",
                    align="R",
                )
                cell(w=W_SPACE, h=None, txt="")
                cell(
                    w=W_NAME,
                    h=None,
                    txt=get(result, "last_name") + " " + get(result, "first_name"),
                    align="L",
                )
                cell(w=W_SPACE, h=None, txt="")
                cell(w=W_YEAR, h=None, txt=str(get(result, "year")), align="R")
                cell(w=W_SPACE, h=None, txt="")
                cell(w=W_CLUB - width, h=None, txt=get(result, "club"), align="L")
                cell(w=W_SPACE, h=None, txt="")
                status = result["result"].status
                if class_.params.otype == "score":
                    if class_.params.apply_handicap_rule:
                        if status == ResultStatus.OK:
                            cell(
                                w=W_VALUE,
                                h=None,
                                txt="{:1.4f}".format(
                                    result["result"].extensions.get("factor", 1)
                                ),
                                align="R",
                            )
                        else:
                            cell(w=W_VALUE, h=None, txt="")
                    print_time(
                        width=W_RUNTIME, time=result["result"].time, status=status
                    )
                    print_points(
                        width=W_VALUE,
                        points=result["result"].extensions.get("score_controls", None),
                        status=status,
                    )
                    print_points(
                        width=W_VALUE,
                        points=result["result"].extensions.get("score_overtime", None),
                        status=status,
                    )
                    print_points_or_status(
                        width=W_TOTAL,
                        points=result["result"].extensions.get("score", None),
                        status=status,
                    )
                else:
                    if (
                        class_.params.penalty_controls is not None
                        or class_.params.penalty_overtime is not None
                        or class_.params.apply_handicap_rule
                    ):
                        print_time(
                            width=W_RUNTIME,
                            time=result["result"].extensions.get("running_time", None),
                            status=status,
                        )
                    if class_.params.penalty_controls is not None:
                        print_time(
                            width=W_VALUE,
                            time=result["result"].extensions.get(
                                "penalties_controls", None
                            ),
                            status=status,
                        )
                    if class_.params.penalty_overtime is not None:
                        print_time(
                            width=W_VALUE,
                            time=result["result"].extensions.get(
                                "penalties_overtime", None
                            ),
                            status=status,
                        )
                    if class_.params.apply_handicap_rule:
                        if status == ResultStatus.OK:
                            cell(
                                w=W_VALUE,
                                h=None,
                                txt="{:1.4f}".format(
                                    result["result"].extensions.get("factor", 1)
                                ),
                                align="R",
                            )
                        else:
                            cell(w=W_VALUE, h=None, txt="")
                    print_time_or_status(
                        width=W_TOTAL, time=result["result"].time, status=status
                    )
                pdf.ln()

    return bytes(pdf.output())

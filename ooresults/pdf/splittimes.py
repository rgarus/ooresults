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


from datetime import datetime
from typing import List
from typing import Tuple
from typing import Optional
from typing import Union

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SplitTime
from ooresults.repo.result_type import SpStatus
from ooresults.pdf.pdf import PDF
from ooresults.utils import globals


def format_result(result: PersonRaceResult, standard: bool):
    def t(a: Optional[datetime], b: Optional[datetime]) -> Optional[int]:
        if a is not None and b is not None:
            diff = b.replace(microsecond=0) - a.replace(microsecond=0)
            return int(diff.total_seconds())
        else:
            return None

    def format_split_time(time: Optional[int]) -> str:
        if time is not None:
            return globals.minutes_seconds(time=time)
        else:
            return "-----"

    if result.start_time is not None and result.finish_time is not None:
        running_time = t(a=result.start_time, b=result.finish_time)
    else:
        running_time = result.extensions.get("running_time", result.time)

    control_code = None
    required = []
    extra = []

    for s in result.split_times:
        if s.status == SpStatus.OK:
            control_code = s.control_code
            required.append(s)
        elif s.status == SpStatus.MISSING:
            required.append(s)
        elif s.status == SpStatus.ADDITIONAL and s.control_code != control_code:
            control_code = s.control_code
            extra.append(s)

    last_time = 0
    for s in required:
        if last_time is not None and s.time is not None:
            split_time = format_split_time(time=int(s.time - last_time))
            last_time = s.time
        else:
            split_time = "-----"

        if standard:
            if s.status == SpStatus.OK and s.time is None:
                yield "ok", "", None
            else:
                if s.leg_voided and split_time != "-----":
                    split_time = f"[{split_time}]"
                yield format_split_time(s.time), split_time, None
        else:
            if s.status == SpStatus.OK and s.time is None:
                yield f"#({s.control_code})", "ok", ""
            else:
                yield (
                    f"#({s.control_code})",
                    format_split_time(s.time),
                    split_time,
                )

    if last_time is not None and running_time is not None:
        split_time = format_split_time(time=int(running_time - last_time))
    else:
        split_time = "-----"
    if standard:
        if result.last_leg_voided and split_time != "-----":
            split_time = "[" + split_time + "]"
        if result.start_time is None and result.finish_time is not None:
            yield "ok", "", None
        else:
            yield format_split_time(running_time), split_time, None
    else:
        if result.start_time is None and result.finish_time is not None:
            yield "F", "ok", ""
        else:
            yield "F", format_split_time(running_time), split_time

    if extra:
        yield "", "", ""
    for s in extra:
        control = f"*({s.control_code})"
        if result.start_time is None or s.punch_time == SplitTime.NO_TIME:
            rel_time = "ok"
        else:
            rel_time = format_split_time(s.time)
        if standard:
            yield rel_time, control, None
        else:
            yield control, rel_time, ""


def create_pdf(
    event: EventType,
    results: List[Tuple[ClassInfoType, List[RankedEntryType]]],
    landscape: bool = False,
) -> bytes:
    # Instantiation of inherited class
    pdf = PDF(name=event.name, landscape=landscape)
    pdf.set_margin(margin=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    nr_split_times = 20 if landscape else 12

    def cell(
        pdf: PDF, w: int, h: Optional[int] = None, txt: str = "", align: str = "L"
    ) -> None:
        while pdf.get_string_width(txt) > w:
            txt = txt[:-1]
        pdf.cell(w=w, h=h, txt=txt, align=align)

    def format_time(time: int, status: ResultStatus) -> str:
        if status == ResultStatus.OK:
            return globals.minutes_seconds(time=time)
        else:
            return pdf.MAP_STATUS[status]

    def pre(pdf: PDF, t1: str = "", t2: str = "", t3: str = "") -> None:
        pdf.set_font(style="B")
        cell(pdf=pdf, w=7, h=None, txt=t1, align="R")
        cell(pdf=pdf, w=2, h=None, txt="")
        cell(pdf=pdf, w=33, h=None, txt=t2, align="L")
        cell(pdf=pdf, w=12, h=None, txt=t3, align="R")
        pdf.set_font(style="")

    for i, class_results in enumerate(results):
        class_, ranked_results = class_results
        standard = class_.params.otype == "standard"

        # filter results - use only finished entries
        ranked_results = [
            r
            for r in ranked_results
            if r.entry.result.status
            not in (
                ResultStatus.INACTIVE,
                ResultStatus.ACTIVE,
                ResultStatus.DID_NOT_START,
            )
        ]

        # do not print classes without entries
        if not ranked_results:
            continue

        if i > 0:
            # insert a page break if there is not enough space left on the
            # page for the class header, the table header and two table rows
            if pdf.will_page_break(height=22):
                pdf.add_page()
            else:
                pdf.ln()
                pdf.ln()

        pdf.set_font(family="Carlito", style="B", size=8)
        pdf.cell(txt=class_.name)

        # print possible voided legs
        if ranked_results and ranked_results[0].entry.result is not None:
            voided_legs = ranked_results[0].entry.result.voided_legs()
            if voided_legs:
                pdf.cell(txt=f'(Voided legs: {", ".join(voided_legs)})')

        # course data
        course_data = pdf.course_data(class_)
        if course_data:
            pdf.set_x(x=max(pdf.get_x() + 12, 67))
            pdf.cell(txt=course_data)

        pdf.ln()
        # add a separator line (1/2 height of a line)
        pdf.ln(0.5 * 0.3515 * 8)

        # print list of control codes as header
        codes = []
        for i, j in enumerate(
            [
                t
                for t in ranked_results[0].entry.result.split_times
                if t.status in [SpStatus.OK, SpStatus.MISSING]
            ]
        ):
            if standard:
                codes.append(f"{str(i+1)}({j.control_code})")
            else:
                codes.append(f"{str(i+1)}")
        codes.append("F")
        for i, j in enumerate(codes):
            if i % nr_split_times == 0:
                if i >= nr_split_times:
                    pdf.ln()
                pre(pdf=pdf)
            cell(pdf=pdf, w=10, h=None, txt=j, align="R")

        pdf.ln()
        pdf.ln()

        ranked = False
        for ranked_result in ranked_results:
            entry = ranked_result.entry
            result = entry.result

            def f(value: Union[Optional[int], Optional[str]]) -> str:
                return str(value) if value is not None else ""

            with pdf.unbreakable() as doc:
                doc.set_font(family="Carlito", size=8)
                if ranked_result.rank is not None:
                    ranked = True
                elif ranked:
                    ranked = False
                    doc.ln()

                sp = 0

                def print_line_1(sp: int, line_1: List[str]) -> None:
                    if sp <= nr_split_times:
                        running_time = result.extensions.get(
                            "running_time", result.time
                        )

                        pre(
                            pdf=doc,
                            t1=f(ranked_result.rank)
                            if not entry.not_competing
                            else "AK",
                            t2=f(entry.last_name) + " " + f(entry.first_name),
                            t3=format_time(running_time, result.status),
                        )
                    else:
                        doc.ln()
                        pre(pdf=doc)

                    for i in line_1:
                        cell(pdf=doc, w=10, h=None, txt=i, align="R")

                def print_line_2(sp: int, line_2: List[str]) -> None:
                    if sp <= nr_split_times:
                        doc.ln()
                        # first line: rank, lastname+firstname, time, splittimes
                        pre(pdf=doc, t2=f(entry.club_name))
                    else:
                        doc.ln()
                        pre(pdf=doc)

                    for i in line_2:
                        cell(pdf=doc, w=10, h=None, txt=i, align="R")

                def print_line_3(sp: int, line_3: List[str]) -> None:
                    doc.ln()
                    pre(pdf=doc)

                    for i in line_3:
                        cell(pdf=doc, w=10, h=None, txt=i, align="R")

                line_1 = []
                line_2 = []
                line_3 = []
                for i, j, k in format_result(result=result, standard=standard):
                    line_1.append(i)
                    line_2.append(j)
                    line_3.append(k)
                    sp += 1
                    if sp % nr_split_times == 0:
                        print_line_1(sp=sp, line_1=line_1)
                        print_line_2(sp=sp, line_2=line_2)
                        if not standard:
                            print_line_3(sp=sp, line_3=line_3)
                        line_1 = []
                        line_2 = []
                        line_3 = []
                if line_1:
                    print_line_1(sp=sp, line_1=line_1)
                    print_line_2(sp=sp, line_2=line_2)
                    if not standard:
                        print_line_3(sp=sp, line_3=line_3)
                doc.ln()

            # add a separator line (1/2 height of a line)
            pdf.ln(0.5 * 0.3515 * 8)

    return bytes(pdf.output())

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
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from typing import Union

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.result_type import SpStatus
from ooresults.pdf.pdf import PDF
from ooresults.utils import globals


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
    nr_splittimes = 20 if landscape else 12

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

    def format_splittime(time: Optional[int]) -> str:
        if time is not None:
            return globals.minutes_seconds(time=time)
        else:
            return "-----"

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
                if t.status != SpStatus.ADDITIONAL
            ]
        ):
            if standard:
                codes.append(f"{str(i+1)}({j.control_code})")
            else:
                codes.append(f"{str(i+1)}")
        codes.append("F")
        for i, j in enumerate(codes):
            if i % nr_splittimes == 0:
                if i >= nr_splittimes:
                    pdf.ln()
                pre(pdf=pdf)
            cell(pdf=pdf, w=10, h=None, txt=j, align="R")

        pdf.ln()
        pdf.ln()

        ranked = False
        for ranked_result in ranked_results:
            entry = ranked_result.entry
            result = entry.result

            def get(d: Dict, key: str) -> str:
                s = d.get(key, "")
                return s if s is not None else ""

            def f(value: Union[Optional[int], Optional[str]]) -> str:
                return str(value) if value is not None else ""

            class Result:
                def __init__(self, result: PersonRaceResult):
                    self.result = result

                def t(
                    self, a: Optional[datetime], b: Optional[datetime]
                ) -> Optional[int]:
                    if a is not None and b is not None:
                        diff = b.replace(microsecond=0) - a.replace(microsecond=0)
                        return int(diff.total_seconds())
                    else:
                        return None

                def next(self) -> str:
                    if (
                        self.result.start_time is not None
                        and self.result.finish_time is not None
                    ):
                        running_time = self.t(
                            a=self.result.start_time, b=self.result.finish_time
                        )
                    else:
                        running_time = self.result.extensions.get(
                            "running_time", self.result.time
                        )

                    last_time = 0
                    for i in [
                        t
                        for t in self.result.split_times
                        if t.status != SpStatus.ADDITIONAL
                    ]:
                        if last_time is not None and i.time is not None:
                            split_time = format_splittime(time=int(i.time - last_time))
                            last_time = i.time
                        else:
                            split_time = "-----"
                        if standard:
                            if i.leg_voided:
                                split_time = "[" + split_time + "]"
                            yield format_splittime(i.time), split_time, None
                        else:
                            yield f"#({i.control_code})", format_splittime(
                                i.time
                            ), split_time

                    if last_time is not None and running_time is not None:
                        split_time = format_splittime(
                            time=int(running_time - last_time)
                        )
                    else:
                        split_time = "-----"
                    if standard:
                        if self.result.last_leg_voided:
                            split_time = "[" + split_time + "]"
                        yield format_splittime(running_time), split_time, None
                    else:
                        yield "F", format_splittime(running_time), split_time
                    additional = [
                        t
                        for t in self.result.split_times
                        if t.status == SpStatus.ADDITIONAL
                    ]
                    if additional != []:
                        yield "", "", ""
                    for i in additional:
                        if standard:
                            yield format_splittime(i.time), f"*({i.control_code})", None
                        else:
                            yield f"*({i.control_code})", format_splittime(i.time), ""

            with pdf.unbreakable() as doc:
                doc.set_font(family="Carlito", size=8)
                if ranked_result.rank is not None:
                    ranked = True
                elif ranked:
                    ranked = False
                    doc.ln()

                sp = 0
                result_data = Result(result=result)

                def print_line_1(sp: int, line_1: List[str]) -> None:
                    if sp <= nr_splittimes:
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
                    if sp <= nr_splittimes:
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
                for i, j, k in result_data.next():
                    line_1.append(i)
                    line_2.append(j)
                    line_3.append(k)
                    sp += 1
                    if sp % nr_splittimes == 0:
                        print_line_1(sp=sp, line_1=line_1)
                        print_line_2(sp=sp, line_2=line_2)
                        if not standard:
                            print_line_3(sp=sp, line_3=line_3)
                        line_1 = []
                        line_2 = []
                        line_3 = []
                if line_1 != []:
                    print_line_1(sp=sp, line_1=line_1)
                    print_line_2(sp=sp, line_2=line_2)
                    if not standard:
                        print_line_3(sp=sp, line_3=line_3)
                doc.ln()

            # add a separator line (1/2 height of a line)
            pdf.ln(0.5 * 0.3515 * 8)

    return bytes(pdf.output())

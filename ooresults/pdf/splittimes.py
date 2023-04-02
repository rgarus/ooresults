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
from typing import Optional

from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.pdf.pdf import PDF
from ooresults.utils import globals


def create_pdf(event: Dict, results: Dict, landscape: bool = False) -> bytes:
    # Instantiation of inherited class
    pdf = PDF(name=event.name, landscape=landscape)
    pdf.set_margin(margin=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    nr_splittimes = 20 if landscape else 12

    def cell(w: int, h: Optional[int] = None, txt: str = "", align: str = "L") -> None:
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

    def pre(t1: str = "", t2: str = "", t3: str = "") -> None:
        pdf.set_font(style="B")
        cell(w=7, h=None, txt=t1, align="R")
        cell(w=2, h=None, txt="")
        cell(w=33, h=None, txt=t2, align="L")
        cell(w=12, h=None, txt=t3, align="R")
        pdf.set_font(style="")

    def t(a: Optional[datetime], b: Optional[datetime]) -> Optional[int]:
        if a is not None and b is not None:
            diff = b.replace(microsecond=0) - a.replace(microsecond=0)
            return int(diff.total_seconds())
        else:
            return None

    for i, class_results in enumerate(results):
        class_, ranked_results = class_results
        standard = class_.params.otype == "standard"

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
        if ranked_results and ranked_results[0]["result"] is not None:
            voided_legs = ranked_results[0]["result"].voided_legs()
            if voided_legs:
                pdf.cell(txt=f'(Voided legs: {", ".join(voided_legs)})')

        pdf.ln()
        # print list of control codes as header
        codes = []
        for i, j in enumerate(
            [
                t
                for t in ranked_results[0]["result"].split_times
                if t.status != "Additional"
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
                pre()
            cell(w=10, h=None, txt=j, align="R")

        pdf.ln()
        pdf.ln()

        ranked = False
        for result in ranked_results:

            def get(d: Dict, key: str) -> str:
                s = d.get(key, "")
                return s if s is not None else ""

            class Result:
                def __init__(self, result: PersonRaceResult):
                    self.result = result

                def next(self) -> str:
                    if (
                        self.result.start_time is not None
                        and self.result.finish_time is not None
                    ):
                        running_time = t(
                            self.result.start_time, self.result.finish_time
                        )
                    else:
                        running_time = self.result.extensions.get(
                            "running_time", self.result.time
                        )

                    last_time = 0
                    for i in [
                        t for t in self.result.split_times if t.status != "Additional"
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
                        t for t in self.result.split_times if t.status == "Additional"
                    ]
                    if additional != []:
                        yield "", "", ""
                    for i in additional:
                        if standard:
                            yield format_splittime(i.time), f"*({i.control_code})", None
                        else:
                            yield f"*({i.control_code})", format_splittime(i.time), ""

            if result["result"].status not in (
                ResultStatus.INACTIVE,
                ResultStatus.DID_NOT_START,
            ):
                pdf.set_font(family="Carlito", size=8)
                if result.rank is not None:
                    ranked = True
                elif ranked:
                    ranked = False
                    pdf.ln()

                sp = 0
                result_data = Result(result=result["result"])

                def print_line_1(sp: int, line_1: List[str]) -> None:
                    if sp <= nr_splittimes:
                        running_time = result["result"].extensions.get(
                            "running_time", result["result"].time
                        )

                        pre(
                            t1=str(get(result, "rank"))
                            if not get(result, "not_competing")
                            else "AK",
                            t2=get(result, "last_name")
                            + " "
                            + get(result, "first_name"),
                            t3=format_time(running_time, result["result"].status),
                        )
                    else:
                        pdf.ln()
                        pre()

                    for i in line_1:
                        cell(w=10, h=None, txt=i, align="R")

                def print_line_2(sp: int, line_2: List[str]) -> None:
                    if sp <= nr_splittimes:
                        pdf.ln()
                        # first line: rank, lastname+firstname, time, splittimes
                        pre(t2=get(result, "club"))
                    else:
                        pdf.ln()
                        pre()

                    for i in line_2:
                        cell(w=10, h=None, txt=i, align="R")

                def print_line_3(sp: int, line_3: List[str]) -> None:
                    pdf.ln()
                    pre()

                    for i in line_3:
                        cell(w=10, h=None, txt=i, align="R")

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
                pdf.ln()

    return bytes(pdf.output())

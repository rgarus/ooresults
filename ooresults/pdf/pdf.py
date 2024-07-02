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


import pathlib
from datetime import datetime

from fpdf import FPDF

from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.result_type import ResultStatus


class PDF(FPDF):
    MAP_STATUS = {
        ResultStatus.INACTIVE: "",
        ResultStatus.ACTIVE: "Started",
        ResultStatus.FINISHED: "Finished",
        ResultStatus.OK: "OK",
        ResultStatus.MISSING_PUNCH: "MP",
        ResultStatus.DID_NOT_START: "DNS",
        ResultStatus.DID_NOT_FINISH: "DNF",
        ResultStatus.OVER_TIME: "OTL",
        ResultStatus.DISQUALIFIED: "DSQ",
    }

    def __init__(self, name: str, landscape: bool = False):
        orientation = "landscape" if landscape else "portrait"
        super().__init__(orientation=orientation)
        self.name = name
        self.creation_time = datetime.now()
        self.set_creator(creator="https://pypi.org/project/ooresults")
        self.set_producer(producer="https://pypi.org/project/ooresults")

        self.fonts_dir = pathlib.Path(__file__).parent / "fonts"
        self.add_font(
            family="Carlito",
            fname=str(self.fonts_dir / "Carlito-Regular.ttf"),
        )
        self.add_font(
            family="Carlito",
            style="B",
            fname=str(self.fonts_dir / "Carlito-Bold.ttf"),
        )
        self.add_font(
            family="Carlito",
            style="I",
            fname=str(self.fonts_dir / "Carlito-Italic.ttf"),
        )
        self.add_font(
            family="Carlito",
            style="BI",
            fname=str(self.fonts_dir / "Carlito-BoldItalic.ttf"),
        )

    def header(self):
        self.set_font(family="Carlito", size=12)
        self.cell(w=0, h=10, txt=self.name, border=1, align="C")
        self.ln(20)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        self.set_font(family="Carlito", size=12)
        # Printing page number
        self.cell(
            w=0, h=10, txt=self.creation_time.strftime("%Y-%m-%d %H:%M:%S"), align="L"
        )
        self.cell(w=0, h=10, txt=f"Page {self.page_no()}/{{nb}}", align="R")

    def course_data(self, class_info: ClassInfoType) -> str:
        #
        # compute course data string:
        # course length - course climb - number of controls
        #
        s = ""
        if class_info.course_length is not None:
            if s != "":
                s += " - "
            s += str(round(class_info.course_length)) + " m"
        if class_info.course_climb is not None:
            if s != "":
                s += " - "
            s += str(round(class_info.course_climb)) + " Hm"
        if (
            class_info.number_of_controls is not None
            and class_info.number_of_controls > 0
        ):
            if s != "":
                s += " - "
            s += str(class_info.number_of_controls) + " Posten"
        return s

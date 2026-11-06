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


from collections.abc import Iterator
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfReader

from webtests.pageobjects.main_page import MainPage


EVENT_NAME = "Test for printing Entries"
EVENT_DATE = "2023-01-15"


@pytest.fixture(scope="module")
def event_for_printing(main_page: MainPage) -> Iterator[str]:
    event_page = main_page.goto_events()
    dialog = event_page.actions.add()
    dialog.enter_values(name=EVENT_NAME, date=EVENT_DATE)
    dialog.submit()
    event_page.select_event(name=EVENT_NAME)
    yield EVENT_NAME
    main_page.goto_events().delete_events()


@pytest.fixture(scope="module")
def import_result_list(main_page: MainPage, event_for_printing: str) -> None:
    class_list_path = Path(__file__).parent.parent / "data" / "ResultList.xml"
    entry_page = main_page.goto_entries(event=event_for_printing)
    dialog = entry_page.actions.import_()
    dialog.format().select(text=dialog.RESULT_LIST)
    dialog.import_file(path=class_list_path)


def test_create_pdf_for_results(
    main_page: MainPage,
    event_for_printing: str,
    import_result_list: None,
    download_dir: Path,
) -> None:
    entry_page = main_page.goto_entries(event=event_for_printing)
    dialog = entry_page.actions.print()
    dialog.print().select(text=dialog.RESULTS)
    t1 = datetime.now()
    document = dialog.create_pdf(download_dir=download_dir)
    t2 = datetime.now()

    reader = PdfReader(BytesIO(document), strict=True)
    assert len(reader.pages) == 1
    page = reader.pages[0]
    text = page.extract_text()

    # exclude the last line (footer), which contains date and time of pdf creation
    assert text.splitlines()[:-1] == [
        "Test for printing Entries",
        "Bahn A - Frauen   (2)",
        "Pl Name Jg Verein Zeit",
        "1 Baerbock Annalena 1980 OC Grün 14:39",
        "2 Faeser Nancy 1970 OC Rot 29:22",
        "Bahn A - Männer   (4)",
        "Pl Name Jg Verein Zeit",
        "1 Lindner Christian 1979 OC Gelb 13:21",
        "2 Scholz Olaf 1958 OC Rot 15:53",
        "3 Buschmann Marco 1977 OC Gelb 17:30",
        "Habeck Robert 1969 OC Grün MP",
    ]

    # check footer
    footer = text.splitlines()[-1]
    create_time = footer[:19]
    t1 = t1.replace(microsecond=0)
    t2 = t2.replace(microsecond=0)
    assert create_time is not None and t1 <= datetime.fromisoformat(create_time) <= t2
    assert footer[19:] == " Page 1/1"


def test_create_pdf_for_split_times(
    main_page: MainPage,
    event_for_printing: str,
    import_result_list: None,
    download_dir: Path,
) -> None:
    entry_page = main_page.goto_entries(event=event_for_printing)
    dialog = entry_page.actions.print()
    dialog.print().select(text=dialog.SPLIT_TIMES)
    t1 = datetime.now()
    document = dialog.create_pdf(download_dir=download_dir)
    t2 = datetime.now()

    reader = PdfReader(BytesIO(document), strict=True)
    assert len(reader.pages) == 1
    page = reader.pages[0]
    text = page.extract_text()

    # exclude the last line (footer), which contains date and time of pdf creation
    assert text.splitlines()[:-1] == [
        "Test for printing Entries",
        "Bahn A - Frauen",
        "1(121) 2(124) 3(122) 4(123) F",
        "1 Baerbock Annalena 14:39 2:09 5:25 8:14 12:00 14:39",
        "OC Grün 2:09 3:16 2:49 3:46 2:39",
        "2 Faeser Nancy 29:22 4:19 17:12 21:17 25:44 29:22",
        "OC Rot 4:19 12:53 4:05 4:27 3:38",
        "Bahn A - Männer",
        "1(121) 2(124) 3(122) 4(123) F",
        "1 Lindner Christian 13:21 1:07 3:10 5:58 8:59 13:21",
        "OC Gelb 1:07 2:03 2:48 3:01 4:22",
        "2 Scholz Olaf 15:53 3:12 6:32 9:04 12:15 15:53",
        "OC Rot 3:12 3:20 2:32 3:11 3:38",
        "3 Buschmann Marco 17:30 1:56 7:12 10:08 14:10 17:30",
        "OC Gelb 1:56 5:16 2:56 4:02 3:20",
        "Habeck Robert MP 2:09 7:00 ----- 10:01 14:04",
        "OC Grün 2:09 4:51 ----- 3:01 4:03",
    ]

    # check footer
    footer = text.splitlines()[-1]
    create_time = footer[:19]
    t1 = t1.replace(microsecond=0)
    t2 = t2.replace(microsecond=0)
    assert create_time is not None and t1 <= datetime.fromisoformat(create_time) <= t2
    assert footer[19:] == " Page 1/1"

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


from ooresults.utils import render
from tests.templates.conftest import Html


def test_tab_buttons() -> None:
    html = Html(text=render.main(events=[]))

    assert len(html.findall(path=".//div[@id='tabs']/button")) == 9
    assert len(html.findall(path=".//button[@id='tab.events']")) == 1
    assert len(html.findall(path=".//button[@id='tab.entries']")) == 1
    assert len(html.findall(path=".//button[@id='tab.classes']")) == 1
    assert len(html.findall(path=".//button[@id='tab.courses']")) == 1
    assert len(html.findall(path=".//button[@id='tab.results']")) == 1
    assert len(html.findall(path=".//button[@id='tab.series']")) == 1
    assert len(html.findall(path=".//button[@id='tab.competitors']")) == 1
    assert len(html.findall(path=".//button[@id='tab.clubs']")) == 1
    assert len(html.findall(path=".//button[@id='tab.reader']")) == 1


def test_events_list_is_empty() -> None:
    html = Html(text=render.main(events=[]))

    assert len(html.findall(path=".//div[@id='tabs']")) == 1
    assert len(html.findall(path=".//div[@id='eve_actions']")) == 1
    assert len(html.findall(path=".//div[@id='entr.actions']")) == 1
    assert len(html.findall(path=".//div[@id='clas.actions']")) == 1
    assert len(html.findall(path=".//div[@id='cour.actions']")) == 1
    assert len(html.findall(path=".//div[@id='comp.actions']")) == 1
    assert len(html.findall(path=".//div[@id='club.actions']")) == 1


def test_upload_button_is_hidden_if_upload_is_not_configured() -> None:
    html = Html(text=render.main(events=[]))

    html.find_not(path=".//button[@id='entr.myBtnUpload']")
    html.find_not(path=".//div[@id='entr.uploadDialog']")


def test_upload_button_is_shown_if_upload_is_configured() -> None:
    html = Html(text=render.main(events=[], upload_name="Munich <O-Cup>"))

    button = html.find(path=".//div[@id='entr.actions']/button[@id='entr.myBtnUpload']")
    assert button.text == "Upload to Munich <O-Cup> ..."
    assert button.attrib["onclick"] == "entr_myUpload()"
    html.find(path=".//div[@id='entr.uploadDialog']//form[@id='entr.upload.form']")

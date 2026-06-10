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

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webtests.pageobjects.classes import ClassPage
from webtests.pageobjects.clubs import ClubPage
from webtests.pageobjects.competitors import CompetitorPage
from webtests.pageobjects.courses import CoursePage
from webtests.pageobjects.entries import EntryPage
from webtests.pageobjects.events import EventPage
from webtests.pageobjects.si_reader import SiReaderPage
from webtests.pageobjects.tabs import Tabs


class MainPage:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.tabs = Tabs(driver=driver)

    def wait(self, timeout: int = 10) -> WebDriverWait:
        return WebDriverWait(
            driver=self.driver,
            timeout=timeout,
            ignored_exceptions=(
                NoSuchElementException,
                StaleElementReferenceException,
            ),
        )

    def load(self) -> None:
        self.driver.get("https://admin:admin@localhost:8080")
        assert "ooresults" in self.driver.title
        elem = self.driver.find_element(By.LINK_TEXT, "Administration")
        elem.click()

    def goto_events(self) -> EventPage:
        if not self.tabs.tab(text="Events").is_selected():
            self.tabs.select(text="Events")
        return EventPage(driver=self.driver)

    def goto_entries(self, event: Optional[str] = None) -> EntryPage:
        if not (
            self.tabs.tab(text="Entries").is_selected()
            and (
                event is None or EntryPage(driver=self.driver).get_event_name() == event
            )
        ):
            if event:
                self.goto_events().select_event(name=event)
            self.tabs.select(text="Entries")
        return EntryPage(driver=self.driver)

    def goto_classes(self, event: Optional[str] = None) -> ClassPage:
        if not (
            self.tabs.tab(text="Classes").is_selected()
            and (
                event is None or ClassPage(driver=self.driver).get_event_name() == event
            )
        ):
            if event:
                self.goto_events().select_event(name=event)
            self.tabs.select(text="Classes")
        return ClassPage(driver=self.driver)

    def goto_courses(self, event: Optional[str] = None) -> CoursePage:
        if not (
            self.tabs.tab(text="Courses").is_selected()
            and (
                event is None
                or CoursePage(driver=self.driver).get_event_name() == event
            )
        ):
            if event:
                self.goto_events().select_event(name=event)
            self.tabs.select(text="Courses")
        return CoursePage(driver=self.driver)

    def goto_competitors(self) -> CompetitorPage:
        if not self.tabs.tab(text="Competitors").is_selected():
            self.tabs.select(text="Competitors")
        return CompetitorPage(driver=self.driver)

    def goto_clubs(self) -> ClubPage:
        if not self.tabs.tab(text="Clubs").is_selected():
            self.tabs.select(text="Clubs")
        return ClubPage(driver=self.driver)

    def goto_si_reader(self, event: Optional[str] = None) -> SiReaderPage:
        if event:
            self.goto_events().select_event(name=event)
        number_of_windows = len(self.driver.window_handles)
        self.tabs.select(text="SI Reader ...")
        WebDriverWait(self.driver, 10).until(
            EC.number_of_windows_to_be(number_of_windows + 1)
        )
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return SiReaderPage(
            driver=self.driver, handle=self.driver.current_window_handle
        )

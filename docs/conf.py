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


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


from multiproject.utils import get_project


# -- Project information -----------------------------------------------------

copyright = "2022, rgarus"
author = "rgarus"
release = "0.4.5"


# -- General configuration ---------------------------------------------------

extensions = [
    "multiproject",
]

# Define the projects that will share this configuration file.
multiproject_projects = {
    "user": {
        "use_config_file": False,
        "config": {
            "project": "ooresults",
        },
    },
    "dev": {
        "use_config_file": False,
        "config": {
            "project": "ooresults-dev",
        },
    },
}

templates_path = ["_templates"]
exclude_patterns = []

current_project = get_project(multiproject_projects)

if current_project == "user":
    language = "de"
elif current_project == "dev":
    language = "en"


# -- Builder options-------- -------------------------------------------------

html_theme = "bizstyle"

latex_elements = {"papersize": "a4paper"}

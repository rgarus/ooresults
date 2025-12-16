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


import io

import bottle
import clevercsv as csv

import ooresults.pdf.series
from ooresults import model
from ooresults.otypes import series_type
from ooresults.utils import render


"""
Handler for the series routes.

/series/update
/series/fill_settings_form
/series/settings
/series/pdfResult
/series/csvResult
"""


@bottle.post("/series/update")
def post_update():
    """Update data."""
    settings, events, results = model.results.build_series_result()
    return render.series_table(events=events, results=results)


@bottle.post("/series/settings")
def post_settings():
    """Update series settings."""
    data = bottle.request.forms
    print(dict(data))
    try:
        settings = series_type.Settings(
            name=data.name,
            nr_of_best_results=(
                int(data.nr_of_best_results) if data.nr_of_best_results != "" else None
            ),
            mode=data.mode,
            maximum_points=int(data.maximum_points),
            decimal_places=int(data.decimal_places),
        )
        model.results.update_series_settings(settings=settings)
    except Exception:
        raise

    settings, events, results = model.results.build_series_result()
    return render.series_table(events=events, results=results)


@bottle.post("/series/pdfResult")
def post_pdf_result():
    """Print series results."""
    data = bottle.request.forms
    landscape = "ser_landscape" in data

    try:
        settings, events, results = model.results.build_series_result()
        content = ooresults.pdf.series.create_pdf(
            settings=settings, events=events, results=results, landscape=landscape
        )
        return content

    except KeyError:
        return bottle.HTTPResponse(status=409, body="Internal error")


@bottle.post("/series/csvResult")
def post_csv_result():
    """Export results as csv for creating diplomas."""
    try:
        settings, events, results = model.results.build_series_result()

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # write header
        writer.writerow(
            [
                "Kategorie",
                "Pos",
                "Pos_eng",
                "Vorname",
                "Nachname",
                "Verein",
                "Punkte",
            ]
        )

        for class_name, series_results in results:
            for ser_result in series_results:
                if ser_result.rank is not None:
                    rank = str(ser_result.rank)
                    if rank == "1":
                        rank_eng = rank + "st"
                    elif rank == "2":
                        rank_eng = rank + "nd"
                    elif rank == "3":
                        rank_eng = rank + "rd"
                    else:
                        rank_eng = rank + "th"

                    def format(value: any) -> str:
                        return str(value) if value is not None else ""

                    writer.writerow(
                        [
                            class_name,
                            rank,
                            rank_eng,
                            format(ser_result.first_name),
                            format(ser_result.last_name),
                            format(ser_result.club_name),
                            format(ser_result.total_points),
                        ]
                    )

        content = output.getvalue()
        output.close()
        return content.encode(encoding="utf-8")

    except KeyError:
        return bottle.HTTPResponse(status=409, body="Internal error")


@bottle.post("/series/fill_settings_form")
def post_fill_settings_form():
    """Query data to fill settings form."""
    settings = model.results.get_series_settings()
    return render.series_settings(settings=settings)

"""
Copyright 2025  Jeff Abrahamson

This file is part of barometre.

barometre is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

barometre is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with barometre.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import os

# from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.views.generic.edit import FormView

from dashboard.forms import FilenameForm
from dashboard.models import GeoPoint, Observation

# JSON_DIRECTORY = "/var/mobilitains/barometre/json/"
JSON_DIRECTORY = "/home/jeff/barometre/"

logger = logging.getLogger("django")


def ingest_observations(filename):
    """Read the specified file and store results.

    The file is assumed to live in JSON_DIRECTORY.

    For each GeoPoint, make sure it exists.  If it doesn't, create it.
    If it exists but isn't the same as the data we're reading, log the
    differences.

    If we are reading a file a second time, we should discover that
    the Observation objects exist and not duplicate them.

    """
    filepath = os.path.join(JSON_DIRECTORY, filename)
    if not os.path.isfile(filepath):
        logger.info(f"File not found: {filepath}")
        return HttpResponseBadRequest("File not found.")

    logger.info(f"Ingesting {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Got JSON data with {len(data)} keys.")

    features = data.get("features", [])
    date_str = data.get("date")
    if not date_str:
        logger.warning("No date found in the file.")
        return

    observed_at = make_aware(parse_datetime(date_str))

    for feature in features:
        props = feature["properties"]
        geom = feature["geometry"]
        insee = props["insee"]

        geopoint, created = GeoPoint.objects.get_or_create(
            insee_code=insee,
            defaults={
                "name": props["name"],
                "population": props["population"],
                "longitude": geom["coordinates"][0],
                "latitude": geom["coordinates"][1],
            },
        )

        if not created:
            diffs = []
            if geopoint.name != props["name"]:
                diffs.append(f"name: {geopoint.name} -> {props['name']}")
            if geopoint.population != props["population"]:
                diffs.append(
                    f"population: {geopoint.population}"
                    f" -> {props['population']}"
                )
            if round(geopoint.longitude, 6) != round(
                geom["coordinates"][0], 6
            ):
                diffs.append(
                    f"longitude: {geopoint.longitude}"
                    f" -> {geom['coordinates'][0]}"
                )
            if round(geopoint.latitude, 6) != round(geom["coordinates"][1], 6):
                diffs.append(
                    f"latitude: {geopoint.latitude} ->"
                    f" {geom['coordinates'][1]}"
                )
            if diffs:
                logger.info(
                    f"GeoPoint {insee} differs from data: " + "; ".join(diffs)
                )

        # Avoid inserting duplicates
        if not Observation.objects.filter(
            geopoint=geopoint, observed_at=observed_at
        ).exists():
            Observation.objects.create(
                geopoint=geopoint,
                observed_at=observed_at,
                contribution_count=props["contributions"],
                percent=props["per_cent"],
            )
        else:
            logger.debug(
                f"Observation already exists for {insee} at {observed_at}"
            )


class IngestView(FormView):
    template_name = "dashboard/ingest_form.html"
    form_class = FilenameForm
    success_url = "."

    def form_valid(self, form):
        filename = form.cleaned_data["filename"].strip()
        logger.info(f"Ingesting {filename}")
        try:
            ingest_observations(filename)
            # return super().form_valid(form)
            return HttpResponse(f"Successfully ingested: {filename}")
        except Exception as e:
            return HttpResponseBadRequest(f"Ingestion failed: {e}")

    def form_invalid(self):
        logger(f"Form not valid: {self.POST}")
        super().form_invalid()

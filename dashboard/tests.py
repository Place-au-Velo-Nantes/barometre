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
import os
from unittest.mock import patch

from django.test import TestCase

from dashboard.models import Commune, Observation
from dashboard.views import ingest_observations

TEST_JSON_DIRECTORY = "/tmp/test_json"  # or use Django's temp dirs


class IngestObservationsTest(TestCase):
    def setUp(self):
        os.makedirs(TEST_JSON_DIRECTORY, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(TEST_JSON_DIRECTORY):
            os.remove(os.path.join(TEST_JSON_DIRECTORY, f))

    def write_test_file(self, filename, content):
        path = os.path.join(TEST_JSON_DIRECTORY, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f)
        return path

    @patch("dashboard.views.JSON_DIRECTORY", TEST_JSON_DIRECTORY)
    def test_create_commune_and_observation(self):
        content = {
            "type": "FeatureCollection",
            "date": "2025-04-03 09:30:01",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [6.2, 45.95]},
                    "properties": {
                        "name": "Testville",
                        "population": 1234,
                        "contributions": 5,
                        "per_cent": 0.42,
                        "insee": "99999",
                    },
                }
            ],
        }
        self.write_test_file("test.geojson", content)

        ingest_observations("test.geojson")

        gp = Commune.objects.get(insee_code="99999")
        self.assertEqual(gp.name, "Testville")
        self.assertEqual(gp.population, 1234)
        self.assertAlmostEqual(gp.latitude, 45.95)
        self.assertEqual(gp.observations.count(), 1)

    @patch("dashboard.views.JSON_DIRECTORY", TEST_JSON_DIRECTORY)
    def test_avoid_duplicate_observations(self):
        content = {
            "type": "FeatureCollection",
            "date": "2025-04-03 09:30:01",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [6.2, 45.95]},
                    "properties": {
                        "name": "Testville",
                        "population": 1234,
                        "contributions": 5,
                        "per_cent": 0.42,
                        "insee": "99999",
                    },
                }
            ],
        }
        self.write_test_file("test.geojson", content)

        # First run
        ingest_observations("test.geojson")
        # Second run should not create duplicates
        ingest_observations("test.geojson")

        self.assertEqual(Commune.objects.count(), 1)
        self.assertEqual(Observation.objects.count(), 1)

    @patch("dashboard.views.JSON_DIRECTORY", TEST_JSON_DIRECTORY)
    def test_log_diff_when_commune_exists(self):
        # Create a Commune with slightly different data
        Commune.objects.create(
            name="Old Name",
            insee_code="99999",
            population=1000,
            longitude=6.0,
            latitude=46.0,
        )

        content = {
            "type": "FeatureCollection",
            "date": "2025-04-03 09:30:01",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [6.2, 45.95]},
                    "properties": {
                        "name": "Testville",
                        "population": 1234,
                        "contributions": 5,
                        "per_cent": 0.42,
                        "insee": "99999",
                    },
                }
            ],
        }
        self.write_test_file("test.geojson", content)

        with self.assertLogs("django", level="INFO") as cm:
            ingest_observations("test.geojson")
        log_output = "\n".join(cm.output)
        self.assertIn("differs from data", log_output)

    @patch("dashboard.views.JSON_DIRECTORY", TEST_JSON_DIRECTORY)
    def test_no_date_in_file(self):
        content = {"type": "FeatureCollection", "features": []}
        self.write_test_file("test.geojson", content)

        with self.assertLogs("django", level="WARNING") as cm:
            ingest_observations("test.geojson")
        self.assertIn("No date found", cm.output[0])

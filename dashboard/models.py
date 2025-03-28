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

from django.db import models


class GeoPoint(models.Model):
    """Represent a geography block."""

    name = models.CharField(max_length=255)
    insee_code = models.CharField(max_length=10, unique=True)
    population = models.PositiveIntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.insee_code})"


class Observation(models.Model):
    """Represent a observations thus far for a GeoPoint."""

    geopoint = models.ForeignKey(
        GeoPoint, on_delete=models.CASCADE, related_name="observations"
    )
    observed_at = models.DateTimeField()
    contribution_count = models.PositiveIntegerField()
    percent = models.FloatField()

    def __str__(self):
        return (
            f"Observation at {self.geopoint.name}"
            f" on {self.observed_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )


def Departement(code):
    """Return a queryset of GeoPoints with given insee_code prefix

    Return a queryset of GeoPoints where the insee_code starts with
    the given department code.

    Parameters:
    code (int or str): Department code (e.g., 44, '2A', '971')

    Returns:
    QuerySet: Filtered GeoPoints

    """
    if isinstance(code, int):
        code_str = str(code).zfill(2)
    elif isinstance(code, str):
        code_str = code.upper()
    else:
        raise ValueError(
            "code must be a 2- or 3-character string or a two-digit integer"
        )

    # Special handling for Corsica and DOM/TOM codes
    valid_prefixes = (
        ["2A", "2B"]
        + [str(i) for i in range(1, 96)]
        + [str(i) for i in range(971, 977)]
    )
    if code_str not in valid_prefixes and not any(
        code_str == str(i).zfill(2) for i in range(96)
    ):
        raise ValueError(f"{code} is not a valid French department code")

    return GeoPoint.objects.filter(insee_code__startswith=code_str)

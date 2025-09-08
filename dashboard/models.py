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


class MapPoint(models.Model):
    """A point feature on a fixed map (parking, incidents, etc.)."""

    year = models.CharField(max_length=4)
    map_name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    commune = models.CharField(max_length=10)  # INSEE code
    epci = models.CharField(max_length=12)
    departement = models.CharField(max_length=3)
    region = models.CharField(max_length=3)
    import_id = models.CharField(max_length=16, default="")
    import_filename = models.CharField(max_length=255, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "year",
                    "map_name",
                    "longitude",
                    "latitude",
                    "commune",
                ],
                name="unique_mappoint",
            )
        ]


class Commune(models.Model):
    """Represent a geography block."""

    year = models.CharField(max_length=4)
    name = models.CharField(max_length=255)
    insee_code = models.CharField(max_length=10, unique=True)
    population = models.PositiveIntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.insee_code})"


class Observation(models.Model):
    """Represent a observations thus far for a Commune."""

    commune = models.ForeignKey(
        Commune, on_delete=models.CASCADE, related_name="observations"
    )
    observed_at = models.DateTimeField()
    contribution_count = models.PositiveIntegerField()
    percent = models.FloatField()

    def __str__(self):
        return (
            f"Observation at {self.commune.name}"
            f" on {self.observed_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )


def Departement(code):
    """Return a queryset of Communes with given insee_code prefix

    Return a queryset of Communes where the insee_code starts with
    the given department code.

    Parameters:
    code (int or str): Department code (e.g., 44, '2A', '971')

    Returns:
    QuerySet: Filtered Communes

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

    return Commune.objects.filter(insee_code__startswith=code_str)

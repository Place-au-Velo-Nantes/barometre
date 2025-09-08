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

from django.contrib import admin

from dashboard.models import Commune, MapPoint, Observation


@admin.register(MapPoint)
class MapPointAdmin(admin.ModelAdmin):
    list_display = (
        "commune",
        "epci",
        "departement",
        "region",
        "longitude",
        "latitude",
    )


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "insee_code",
        "population",
        "latitude",
        "longitude",
    )
    search_fields = ("name", "insee_code")
    list_filter = ("population",)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        "commune",
        "observed_at",
        "contribution_count",
        "percent",
    )
    list_filter = ("observed_at",)
    search_fields = ("commune__name", "commune__insee_code")
    autocomplete_fields = ["commune"]
    date_hierarchy = "observed_at"

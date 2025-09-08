import json
import logging
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import zstandard

from dashboard.models import MapPoint

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Import map data from a zstandard-compressed GeoJSON file."""

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "file", help="Path to zstd-compressed GeoJSON file"
        )
        parser.add_argument("year", help="Year associated with the data")
        parser.add_argument("map_name", help="Map name for these points")

    def handle(self, *args, **options):
        file_path = Path(options["file"]).expanduser()
        year = options["year"]
        map_name = options["map_name"]

        if not file_path.exists():
            raise CommandError(f"File {file_path} does not exist")

        import_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        import_filename = file_path.name

        try:
            dctx = zstandard.ZstdDecompressor()
            with file_path.open("rb") as fh:
                with dctx.stream_reader(fh) as reader:
                    data = json.loads(reader.read())
        except Exception as exc:  # pragma: no cover - error path
            raise CommandError(f"Could not read {file_path}: {exc}") from exc

        features = data.get("features", [])
        total = len(features)

        existing = set(
            MapPoint.objects.filter(year=year, map_name=map_name).values_list(
                "longitude", "latitude", "commune"
            )
        )

        to_create = []
        duplicates = []
        seen = set()

        for feature in features:
            try:
                lon, lat = feature["geometry"]["coordinates"]
                props = feature.get("properties", {})
                commune = props.get("commune") or props.get("insee") or ""
                epci = props.get("epci", "")
                departement = props.get("departement", "")
                region = props.get("region", "")
            except Exception as exc:  # pragma: no cover - malformed feature
                logger.warning("Skipping malformed feature: %s", exc)
                continue

            key = (lon, lat, commune)
            if key in existing or key in seen:
                duplicates.append(key)
                continue
            seen.add(key)

            to_create.append(
                MapPoint(
                    year=year,
                    map_name=map_name,
                    longitude=lon,
                    latitude=lat,
                    commune=commune,
                    epci=epci,
                    departement=departement,
                    region=region,
                    import_id=import_id,
                    import_filename=import_filename,
                )
            )

        dup_count = len(duplicates)
        if total and dup_count == total:
            self.stdout.write("All records already imported; nothing to do.")
            return

        if total and dup_count > total * 0.5:
            raise CommandError(
                f"{dup_count} out of {total} records already exist. "
                f"Example duplicates: {duplicates[:5]}"
            )

        with transaction.atomic():
            MapPoint.objects.bulk_create(to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(to_create)} records; "
                f"{dup_count} duplicates skipped."
            )
        )
        if duplicates:
            logger.info(
                "Duplicate records skipped: %s", duplicates[:5]
            )

# scripts/management/commands/load_seeds.py
import json
from pathlib import Path
from typing import Optional, Tuple

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from scripts.models import TemplateStyle, TitleTone, Tone
from scripts.seeds_utils import DEFAULT_SEEDS_ROOT

ModelT = {
    "tones": Tone,
    "template_styles": TemplateStyle,
    "title_tones": TitleTone,
}

UNIQUE_HINTS = {
    # Prefer a stable lookup key per model. Adjust to match your models.
    "Tone": ("slug", "name"),
    "TemplateStyle": ("slug", "name"),
    "TitleTone": ("slug", "name"),
}


def _find_lookup_field(model_name: str, payload: dict) -> Optional[Tuple[str, str]]:
    """
    Determine which field to use for finding an existing record.
    Priority:
    1. Use _natural_key if present
    2. Fall back to model-specific UNIQUE_HINTS
    """
    nk = payload.get("_natural_key")
    if isinstance(nk, dict) and nk.get("field") and nk.get("value"):
        return nk["field"], nk["value"]

    for field in UNIQUE_HINTS.get(model_name, ()):
        if field in payload and payload[field]:
            return field, payload[field]
    return None


def _apply_fields(obj, payload: dict):
    """Apply simple and M2M fields from payload onto model instance."""
    payload = {k: v for k, v in payload.items() if k not in {"_natural_key"}}

    # Separate M2M relations
    m2m_values = {}
    for m2m in obj._meta.many_to_many:
        if m2m.name in payload:
            m2m_values[m2m.name] = payload.pop(m2m.name)

    # Assign simple fields
    for k, v in payload.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

    obj.save()

    # Assign M2M by PK list
    for field_name, pks in m2m_values.items():
        getattr(obj, field_name).set(pks)


class Command(BaseCommand):
    help = "Load JSON seed files (per-record) from seeds/ into the DB. Idempotent and skips already-existing entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--models",
            nargs="*",
            choices=["Tone", "TemplateStyle", "TitleTone"],
            help="Limit to specific models",
        )
        parser.add_argument(
            "--seeds-root",
            type=str,
            help="Custom seeds root path (defaults to settings.SEEDS_ROOT or BASE_DIR/seeds)",
        )
        parser.add_argument(
            "--update-only",
            action="store_true",
            help="Do not create missing records; update existing ones only.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        seeds_root = Path(options["seeds_root"] or DEFAULT_SEEDS_ROOT)
        models_filter = set(options["models"] or ["Tone", "TemplateStyle", "TitleTone"])
        update_only = options["update_only"]

        if not seeds_root.exists():
            self.stderr.write(self.style.ERROR(f"Seeds folder not found: {seeds_root}"))
            return

        total_upserted = 0

        for dir_key, Model in ModelT.items():
            model_name = Model.__name__
            if model_name not in models_filter:
                continue

            folder = seeds_root / dir_key
            if not folder.exists():
                self.stdout.write(
                    self.style.WARNING(f"Skip {model_name}: {folder} not found")
                )
                continue

            files = sorted(folder.glob("*.json"))
            upserted = 0

            for fp in files:
                payload = json.loads(fp.read_text(encoding="utf-8"))
                lookup = _find_lookup_field(model_name, payload)
                obj = None

                if lookup:
                    field, value = lookup
                    obj = Model.objects.filter(**{field: value}).first()

                # Skip if record already exists
                if obj is not None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[skip-existing] {model_name} '{fp.stem}' already exists"
                        )
                    )
                    continue

                # If update-only mode, skip creating new records
                if update_only:
                    self.stdout.write(
                        self.style.WARNING(f"[skip-create] {model_name} from {fp.name}")
                    )
                    continue

                try:
                    obj = Model()
                except IntegrityError as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"IntegrityError creating {model_name} from {fp.name}: {e}"
                        )
                    )
                    continue

                _apply_fields(obj, payload)
                upserted += 1

            total_upserted += upserted
            self.stdout.write(
                self.style.SUCCESS(f"Upserted {upserted} {model_name} records")
            )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Done. Total upserted: {total_upserted}")
        )

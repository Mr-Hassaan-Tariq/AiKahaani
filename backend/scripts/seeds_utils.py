# scripts/seed_utils.py
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.forms.models import model_to_dict

DEFAULT_SEEDS_ROOT = Path(getattr(settings, "SEEDS_ROOT", settings.BASE_DIR / "seeds"))

MODEL_DIR_MAP = {
    "Tone": "tones",
    "TemplateStyle": "template_styles",
    "TitleTone": "title_tones",
}

EXCLUDE_FIELDS = {"id", "pk", "created_at", "updated_at"}  # adjust if you use these


def _dir_for_model(model: type[Model]) -> Path:
    name = model.__name__
    if name not in MODEL_DIR_MAP:
        raise ValueError(f"No seeds directory mapping for model {name}")
    return DEFAULT_SEEDS_ROOT / MODEL_DIR_MAP[name]


def _filename_for_instance(instance: Model) -> str:
    """
    Prefer a stable identifier. If your models have `slug`, use it.
    Otherwise, fall back to `name` or the pk.
    """
    for attr in ("slug", "key", "code", "name"):
        if hasattr(instance, attr) and getattr(instance, attr):
            safe = str(getattr(instance, attr)).strip().lower().replace(" ", "-")
            return f"{safe}.json"
    return f"{instance.pk}.json"


def _serialize_instance(instance: Model) -> Dict[str, Any]:
    data = model_to_dict(instance)
    for f in EXCLUDE_FIELDS:
        data.pop(f, None)

    # Handle M2M explicitly so files are stable
    for m2m in instance._meta.many_to_many:
        field_name = m2m.name
        data[field_name] = list(
            getattr(instance, field_name).values_list("pk", flat=True)
        )

    # Also persist a stable unique key if present (helpful when importing)
    for candidate in ("slug", "key", "code", "name"):
        if candidate in data:
            data["_natural_key"] = {"field": candidate, "value": data[candidate]}
            break

    return data


def write_seed_file(instance: Model) -> Path:
    target_dir = _dir_for_model(instance.__class__)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / _filename_for_instance(instance)
    payload = _serialize_instance(instance)
    file_path.write_text(
        json.dumps(payload, cls=DjangoJSONEncoder, indent=2), encoding="utf-8"
    )
    return file_path


def write_seed_files(instances: Iterable[Model]) -> list[Path]:
    paths = []
    for inst in instances:
        paths.append(write_seed_file(inst))
    return paths

# scripts/management/commands/dump_seeds.py
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from scripts.models import TemplateStyle, TitleTone, Tone
from scripts.seeds_utils import (
    DEFAULT_SEEDS_ROOT,
    _dir_for_model,
    _filename_for_instance,
)


class Command(BaseCommand):
    help = "Dump all existing Tone, TemplateStyle, and TitleTone data into JSON files inside seeds/. Skips existing files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--models",
            nargs="*",
            choices=["Tone", "TemplateStyle", "TitleTone"],
            help="Limit to specific models",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=str(DEFAULT_SEEDS_ROOT),
            help="Base output directory for seed JSONs (default: settings.SEEDS_ROOT or BASE_DIR/seeds)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing JSON files instead of skipping them.",
        )

    def handle(self, *args, **options):
        models = options["models"] or ["Tone", "TemplateStyle", "TitleTone"]
        output = Path(options["output"])
        force = options["force"]

        self.stdout.write(self.style.HTTP_INFO(f"Dumping seeds to {output}"))
        output.mkdir(parents=True, exist_ok=True)

        total_files = 0
        skipped = 0

        def dump_model_records(model_class, model_name: str):
            nonlocal total_files, skipped
            model_dir = _dir_for_model(model_class)
            model_dir.mkdir(parents=True, exist_ok=True)

            instances = model_class.objects.all().order_by("id")

            for instance in instances:
                filename = _filename_for_instance(instance)
                file_path = model_dir / filename

                if file_path.exists() and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[skip-existing] {model_name} '{filename}' already exists"
                        )
                    )
                    skipped += 1
                    continue

                # Write the seed JSON
                from django.core.serializers.json import DjangoJSONEncoder
                from django.forms.models import model_to_dict

                data = model_to_dict(instance)
                for field in ["id", "pk", "created_at", "updated_at"]:
                    data.pop(field, None)

                file_path.write_text(
                    json.dumps(data, cls=DjangoJSONEncoder, indent=2), encoding="utf-8"
                )

                self.stdout.write(
                    self.style.SUCCESS(f"[write] {model_name} -> {filename}")
                )
                total_files += 1

        if "Tone" in models:
            dump_model_records(Tone, "Tone")

        if "TemplateStyle" in models:
            dump_model_records(TemplateStyle, "TemplateStyle")

        if "TitleTone" in models:
            dump_model_records(TitleTone, "TitleTone")

        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 Dump complete — {total_files} new JSON files written, {skipped} skipped."
            )
        )

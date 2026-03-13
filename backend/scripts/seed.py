"""
Seed script — populates lookup tables on first run.

Safe to run on every deploy: uses ON CONFLICT DO NOTHING so existing rows
are untouched. Typically invoked automatically via the Railway start command:

    alembic upgrade head && python scripts/seed.py && gunicorn ...

Can also be run manually:

    python scripts/seed.py
    python scripts/seed.py --dry-run      # show what would be inserted
    python scripts/seed.py --verbose      # show skipped rows too
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# ── Project root on sys.path so `app.*` imports work ─────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Minimal env so config doesn't blow up — DATABASE_URL must be real or set
# via environment before running this script.
os.environ.setdefault("SECRET_KEY", "seed-script-placeholder")

from sqlalchemy.dialects.postgresql import insert  # noqa: E402

from app.database import AsyncSessionLocal  # noqa: E402
from app.models.script import TemplateStyle, Tone, ToneScope  # noqa: E402


# ── Seed data ─────────────────────────────────────────────────────────────────

SCRIPT_TONES = [
    "Informative",
    "Professional",
    "Entertaining",
    "Motivational",
    "Funny",
]

TITLE_TONES = [
    "Controversial",
    "Shocking",
    "Persuasive",
    "Mysterious",
    "Dramatic",
    "Question-based",
    "Sarcastic",
    "Witty",
    "Neutral",
    "Educational",
    "Inspirational",
    "Urgent",
]

TEMPLATE_STYLES = [
    {
        "name": "Short",
        "min_length": 2800,
        "max_length": 3000,
        "duration": 20,
        "outline_sections": 4,
        "description": "Great for concise explainers or presentations (~20 min at 140 WPM)",
    },
    {
        "name": "Medium",
        "min_length": 5600,
        "max_length": 6000,
        "duration": 40,
        "outline_sections": 6,
        "description": "Ideal for in-depth videos, product demos, interviews (~40 min at 140 WPM)",
    },
    {
        "name": "Long",
        "min_length": 8400,
        "max_length": 9000,
        "duration": 60,
        "outline_sections": 8,
        "description": "Best for comprehensive tutorials, webinars, lectures (~60 min at 140 WPM)",
    },
]


# ── Seed functions ────────────────────────────────────────────────────────────

async def seed_tones(session, dry_run: bool, verbose: bool) -> int:
    inserted = 0

    for name in SCRIPT_TONES:
        if dry_run:
            print(f"  [dry-run] Tone (script): {name}")
            continue
        stmt = (
            insert(Tone)
            .values(name=name, scope=ToneScope.script)
            .on_conflict_do_nothing(constraint="uq_tones_name_scope")
        )
        result = await session.execute(stmt)
        if result.rowcount:
            print(f"  + Tone (script): {name}")
            inserted += 1
        elif verbose:
            print(f"  ~ skip (exists): Tone (script): {name}")

    for name in TITLE_TONES:
        if dry_run:
            print(f"  [dry-run] Tone (title): {name}")
            continue
        stmt = (
            insert(Tone)
            .values(name=name, scope=ToneScope.title)
            .on_conflict_do_nothing(constraint="uq_tones_name_scope")
        )
        result = await session.execute(stmt)
        if result.rowcount:
            print(f"  + Tone (title): {name}")
            inserted += 1
        elif verbose:
            print(f"  ~ skip (exists): Tone (title): {name}")

    return inserted


async def seed_template_styles(session, dry_run: bool, verbose: bool) -> int:
    inserted = 0

    for style in TEMPLATE_STYLES:
        if dry_run:
            print(f"  [dry-run] TemplateStyle: {style['name']}")
            continue
        stmt = (
            insert(TemplateStyle)
            .values(**style)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        result = await session.execute(stmt)
        if result.rowcount:
            print(f"  + TemplateStyle: {style['name']}")
            inserted += 1
        elif verbose:
            print(f"  ~ skip (exists): TemplateStyle: {style['name']}")

    return inserted


# ── Entry point ───────────────────────────────────────────────────────────────

async def main(dry_run: bool, verbose: bool) -> None:
    print("=" * 50)
    print("Video Scripts — seed script")
    if dry_run:
        print("DRY RUN — no changes will be written")
    print("=" * 50)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("\nSeeding tones...")
            tones_inserted = await seed_tones(session, dry_run, verbose)

            print("\nSeeding template styles...")
            styles_inserted = await seed_template_styles(session, dry_run, verbose)

    if dry_run:
        print("\nDry run complete — re-run without --dry-run to apply.")
    else:
        print(
            f"\nDone. Inserted {tones_inserted} tone(s), "
            f"{styles_inserted} template style(s). "
            f"Existing rows were left untouched."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed lookup tables")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be inserted without writing to the DB",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also print rows that were skipped (already exist)",
    )
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run, verbose=args.verbose))

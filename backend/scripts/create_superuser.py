"""
Create or promote a super_admin user.

Usage (CLI args):
    python scripts/create_superuser.py \\
        --email admin@example.com \\
        --username admin \\
        --password secret123

Usage (environment variables):
    SUPERUSER_EMAIL=admin@example.com \\
    SUPERUSER_USERNAME=admin \\
    SUPERUSER_PASSWORD=secret123 \\
    python scripts/create_superuser.py

If the email already exists the user is promoted to super_admin (no duplicate
is created). Idempotent — safe to run multiple times.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# ── Project root on sys.path ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("SECRET_KEY", "seed-script-placeholder")

from sqlalchemy import select  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.database import AsyncSessionLocal  # noqa: E402
from app.models.user import User, UserPlan, UserRole  # noqa: E402


async def create_superuser(email: str, username: str, password: str) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.email == email))
            existing = result.scalar_one_or_none()

            if existing:
                if existing.role == UserRole.super_admin:
                    print(f"User '{email}' is already a super_admin. No changes made.")
                else:
                    existing.role = UserRole.super_admin
                    print(f"Promoted existing user '{email}' to super_admin.")
                return

            user = User(
                email=email,
                username=username,
                password_hash=hash_password(password),
                role=UserRole.super_admin,
                plan=UserPlan.free,
                is_active=True,
                is_email_verified=True,
            )
            session.add(user)
            print(f"Created super_admin user: {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a super_admin user")
    parser.add_argument(
        "--email",
        default=os.environ.get("SUPERUSER_EMAIL"),
        help="Email address (or set SUPERUSER_EMAIL env var)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("SUPERUSER_USERNAME"),
        help="Username (or set SUPERUSER_USERNAME env var)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("SUPERUSER_PASSWORD"),
        help="Password (or set SUPERUSER_PASSWORD env var)",
    )
    args = parser.parse_args()

    missing = [f for f, v in [("--email", args.email), ("--username", args.username), ("--password", args.password)] if not v]
    if missing:
        print(f"Error: missing required arguments: {', '.join(missing)}")
        print("Provide them as CLI args or set SUPERUSER_EMAIL / SUPERUSER_USERNAME / SUPERUSER_PASSWORD.")
        sys.exit(1)

    asyncio.run(create_superuser(args.email, args.username, args.password))


if __name__ == "__main__":
    main()

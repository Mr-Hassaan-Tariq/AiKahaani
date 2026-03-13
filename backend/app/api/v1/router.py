"""
Version 1 API router.

All v1 sub-routers are registered here. This module is mounted at /api/v1
in main.py. When v2 is needed, create app/api/v2/router.py and mount it
at /api/v2 — zero changes required in existing v1 routes.
"""

from fastapi import APIRouter

from app.api.v1.admin.router import admin_router
from app.api.v1.affiliates.router import affiliates_router
from app.api.v1.niches.router import niches_router
from app.api.v1.notifications.router import notifications_router
from app.api.v1.scripts.router import scripts_router
from app.api.v1.users.router import users_router

v1_router = APIRouter()

v1_router.include_router(scripts_router, prefix="/scripts")
v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(niches_router, prefix="/niches")
v1_router.include_router(notifications_router, prefix="/notifications")
v1_router.include_router(affiliates_router, prefix="/affiliates")
v1_router.include_router(admin_router, prefix="/admin")

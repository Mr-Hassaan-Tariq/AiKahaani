"""
Affiliates router — /api/v1/affiliates/*

Endpoints:
  POST /click   — track referral link click (no auth required)

Internal helpers (not endpoints, called from auth flow):
  - tolt_client.create_customer()
  - tolt_client.report_transaction()
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.core.responses import responses
from app.schemas.affiliate import TrackClickRequest, TrackClickResponse
from app.schemas.common import ApiResponse
from app.services.affiliates.tolt_client import ToltAPIError, tolt_client

logger = logging.getLogger(__name__)

affiliates_router = APIRouter(tags=["Affiliates"])


@affiliates_router.post("/click", response_model=ApiResponse[TrackClickResponse])
async def track_referral_click(body: TrackClickRequest):
    """
    Track a referral link click and resolve the partner_id.

    Called by the frontend when a user lands on the site with ?via=REFERRAL_CODE.
    Returns the partner_id which the frontend stores in localStorage to pass during signup.
    No authentication required.
    """
    if not tolt_client.is_enabled():
        logger.warning("[AFFILIATES] Tolt not configured — returning empty response")
        return responses.ok(
            data=TrackClickResponse(
                partner_id=None,
                referral_code=body.referral_code,
                message="Affiliate tracking not configured",
            ),
            message="Affiliate tracking not configured",
        )

    try:
        click_data = await tolt_client.track_click(
            referral_code=body.referral_code,
            page_url=body.page_url,
            device_type=body.device_type,
            param_name=body.param_name,
        )
        partner_id = click_data.get("partner_id")
        if not partner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid referral code",
            )

        logger.info(
            "[AFFILIATES] Click tracked: referral_code=%s partner_id=%s",
            body.referral_code,
            partner_id,
        )
        return responses.ok(
            data=TrackClickResponse(
                partner_id=partner_id,
                referral_code=body.referral_code,
                message="Click tracked successfully",
            ),
            message="Click tracked successfully",
        )

    except ToltAPIError as e:
        logger.error("[AFFILIATES] Tolt error tracking click: %s", e.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to track referral click",
        )

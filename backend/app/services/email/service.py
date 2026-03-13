"""
Email service — sends transactional emails via Brevo REST API.

Uses httpx (async) instead of an SDK so there are no extra dependencies.
All methods are fire-and-forget friendly: they log errors but don't raise,
so a failed email never aborts the auth flow that triggered it.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_BREVO_URL = "https://api.brevo.com/v3/smtp/email"


async def _send(subject: str, html: str, plain: str, to_email: str, to_name: str) -> bool:
    """
    Low-level helper that POSTs to the Brevo transactional email API.
    Returns True on success, False on failure.
    """
    if not settings.brevo_api_key or settings.brevo_api_key == "placeholder":
        logger.warning("Brevo API key not configured — skipping email to %s", to_email)
        return False

    payload = {
        "sender": {"name": "Video Scripts", "email": settings.default_from_email},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html,
        "textContent": plain,
    }
    headers = {
        "api-key": settings.brevo_api_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(_BREVO_URL, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info("Email sent to %s: %s", to_email, subject)
            return True
    except httpx.HTTPStatusError as e:
        logger.error(
            "Brevo API error sending to %s: %s %s",
            to_email,
            e.response.status_code,
            e.response.text,
        )
        return False
    except Exception as e:
        logger.error("Email send failed to %s: %s", to_email, str(e))
        return False


async def send_magic_link_email(
    to_email: str,
    user_name: str,
    magic_link: str,
    is_new_user: bool,
) -> bool:
    """Send the magic link email for login or signup."""
    action = "sign up" if is_new_user else "log in"
    subject = "👉 Your Video Scripts Access Link"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2>Hello {user_name}!</h2>
      <p>Click the link below to {action} to Video Scripts. This link expires in <strong>30 minutes</strong>.</p>
      <p style="margin: 24px 0;">
        <a href="{magic_link}"
           style="background:#6366f1;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">
          {action.title()} to Video Scripts
        </a>
      </p>
      <p style="color:#888;font-size:12px;">
        If you didn't request this, you can safely ignore this email.
        This link can only be used once.
      </p>
    </div>
    """
    plain = (
        f"Hello {user_name}!\n\n"
        f"Click the link below to {action} to Video Scripts (expires in 30 minutes):\n\n"
        f"{magic_link}\n\n"
        "If you didn't request this, ignore this email."
    )
    return await _send(subject, html, plain, to_email, user_name)


async def send_email_verification(
    to_email: str,
    user_name: str,
    verify_url: str,
) -> bool:
    """Send the email verification link after an email address change."""
    subject = "Verify your Video Scripts email address"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2>Verify your email, {user_name}!</h2>
      <p>You recently changed your email address. Click below to verify it.
         This link expires in <strong>24 hours</strong>.</p>
      <p style="margin: 24px 0;">
        <a href="{verify_url}"
           style="background:#6366f1;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">
          Verify Email Address
        </a>
      </p>
      <p style="color:#888;font-size:12px;">
        If you didn't make this change, please contact support immediately.
      </p>
    </div>
    """
    plain = (
        f"Hello {user_name}!\n\n"
        "Please verify your new email address by clicking the link below "
        "(expires in 24 hours):\n\n"
        f"{verify_url}\n\n"
        "If you didn't request this change, contact support immediately."
    )
    return await _send(subject, html, plain, to_email, user_name)

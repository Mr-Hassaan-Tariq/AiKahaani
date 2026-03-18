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


async def _send(
    subject: str, html: str, plain: str, to_email: str, to_name: str
) -> bool:
    """
    Low-level helper that POSTs to the Brevo transactional email API.
    Returns True on success, False on failure.
    """
    print(settings.brevo_api_key)
    if not settings.brevo_api_key or settings.brevo_api_key == "placeholder":
        logger.warning("Brevo API key not configured — skipping email to %s", to_email)
        return False

    payload = {
        "sender": {"name": "AIKahaani", "email": settings.default_from_email},
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
    subject = "Your AIKahaani Access Link"
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background-color:#f4f4f5;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;padding:40px 16px;">
        <tr>
          <td align="center">
            <table width="100%" style="max-width:560px;" cellpadding="0" cellspacing="0">

              <!-- Logo header -->
              <tr>
                <td align="center" style="padding-bottom:24px;">
                  <span style="font-size:22px;font-weight:900;letter-spacing:-0.5px;color:#111827;">
                    AI<span style="color:#dc2626;">Kahaani</span>
                  </span>
                </td>
              </tr>

              <!-- Card -->
              <tr>
                <td style="background-color:#ffffff;border-radius:16px;padding:40px 36px;border:1px solid #e5e7eb;">

                  <!-- Badge -->
                  <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background-color:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:8px 14px;">
                        <span style="font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#dc2626;">
                          {'New Account' if is_new_user else 'Welcome Back'}
                        </span>
                      </td>
                    </tr>
                  </table>

                  <!-- Heading -->
                  <h1 style="margin:0 0 12px;font-size:26px;font-weight:800;color:#111827;letter-spacing:-0.5px;line-height:1.2;">
                    Hello, {user_name}!
                  </h1>

                  <!-- Body -->
                  <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#6b7280;">
                    Click the button below to {action} to AIKahaani.
                    This link expires in <strong style="color:#111827;">30 minutes</strong> and can only be used once.
                  </p>

                  <!-- CTA button -->
                  <table cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                    <tr>
                      <td style="border-radius:8px;background-color:#dc2626;">
                        <a href="{magic_link}"
                           style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:8px;letter-spacing:0.01em;">
                          {action.title()} to AIKahaani &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Divider -->
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 24px;">

                  <!-- Fallback link -->
                  <p style="margin:0 0 6px;font-size:12px;color:#9ca3af;">
                    Or copy this link into your browser:
                  </p>
                  <p style="margin:0;font-size:11px;color:#6b7280;word-break:break-all;">
                    {magic_link}
                  </p>

                </td>
              </tr>

              <!-- Footer note -->
              <tr>
                <td style="padding-top:24px;" align="center">
                  <p style="margin:0;font-size:12px;color:#9ca3af;">
                    If you didn't request this, you can safely ignore this email.
                  </p>
                  <p style="margin:8px 0 0;font-size:11px;color:#d1d5db;">
                    &copy; 2025 AIKahaani. All rights reserved.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    plain = (
        f"Hello {user_name}!\n\n"
        f"Click the link below to {action} to AIKahaani (expires in 30 minutes):\n\n"
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
    subject = "Verify your AIKahaani email address"
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background-color:#f4f4f5;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;padding:40px 16px;">
        <tr>
          <td align="center">
            <table width="100%" style="max-width:560px;" cellpadding="0" cellspacing="0">

              <!-- Logo header -->
              <tr>
                <td align="center" style="padding-bottom:24px;">
                  <span style="font-size:22px;font-weight:900;letter-spacing:-0.5px;color:#111827;">
                    AI<span style="color:#dc2626;">Kahaani</span>
                  </span>
                </td>
              </tr>

              <!-- Card -->
              <tr>
                <td style="background-color:#ffffff;border-radius:16px;padding:40px 36px;border:1px solid #e5e7eb;">

                  <!-- Badge -->
                  <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background-color:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:8px 14px;">
                        <span style="font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#dc2626;">
                          Email Verification
                        </span>
                      </td>
                    </tr>
                  </table>

                  <!-- Heading -->
                  <h1 style="margin:0 0 12px;font-size:26px;font-weight:800;color:#111827;letter-spacing:-0.5px;line-height:1.2;">
                    Verify your email, {user_name}!
                  </h1>

                  <!-- Body -->
                  <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#6b7280;">
                    You recently changed your email address. Click the button below to verify it.
                    This link expires in <strong style="color:#111827;">24 hours</strong>.
                  </p>

                  <!-- CTA button -->
                  <table cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                    <tr>
                      <td style="border-radius:8px;background-color:#dc2626;">
                        <a href="{verify_url}"
                           style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:8px;letter-spacing:0.01em;">
                          Verify Email Address &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Divider -->
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 24px;">

                  <!-- Fallback link -->
                  <p style="margin:0 0 6px;font-size:12px;color:#9ca3af;">
                    Or copy this link into your browser:
                  </p>
                  <p style="margin:0;font-size:11px;color:#6b7280;word-break:break-all;">
                    {verify_url}
                  </p>

                </td>
              </tr>

              <!-- Footer note -->
              <tr>
                <td style="padding-top:24px;" align="center">
                  <p style="margin:0;font-size:12px;color:#9ca3af;">
                    If you didn't make this change, please contact support immediately.
                  </p>
                  <p style="margin:8px 0 0;font-size:11px;color:#d1d5db;">
                    &copy; 2025 AIKahaani. All rights reserved.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    plain = (
        f"Hello {user_name}!\n\n"
        "Please verify your new email address by clicking the link below "
        "(expires in 24 hours):\n\n"
        f"{verify_url}\n\n"
        "If you didn't request this change, contact support immediately."
    )
    return await _send(subject, html, plain, to_email, user_name)

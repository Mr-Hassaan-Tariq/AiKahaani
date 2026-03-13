"""
Async Tolt API client.

Handles all HTTP communication with the Tolt affiliate REST API.
Uses httpx.AsyncClient — drop-in async replacement for the Django requests-based client.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ToltAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ToltAPIClient:
    def __init__(self) -> None:
        self.api_key = settings.tolt_api_key
        self.base_url = settings.tolt_api_base_url.rstrip("/")
        self.timeout = 30.0

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def _request(self, method: str, endpoint: str, data: Dict[str, Any]) -> Dict:
        url = f"{self.base_url}{endpoint}"
        logger.info("[TOLT_API] %s %s | body=%s", method, endpoint, data)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.request(method, url, json=data, headers=self._headers())
            except httpx.TimeoutException:
                raise ToltAPIError("Tolt API request timed out")
            except httpx.ConnectError as e:
                raise ToltAPIError(f"Failed to connect to Tolt API: {e}")

        logger.info("[TOLT_API] Response [%d]: %s", resp.status_code, resp.text[:500])

        try:
            resp_data = resp.json()
        except Exception:
            resp_data = {}

        if resp.status_code >= 400:
            msg = resp_data.get("message") or resp_data.get("error") or "Tolt API error"
            raise ToltAPIError(msg, status_code=resp.status_code)

        return resp_data

    async def track_click(
        self,
        referral_code: str,
        page_url: str,
        device_type: str = "desktop",
        param_name: str = "via",
    ) -> Dict:
        """POST /clicks — track a referral link click."""
        data = {
            "param": param_name,
            "value": referral_code,
            "page": page_url,
            "device": device_type,
        }
        resp_data = await self._request("POST", "/clicks", data)
        if resp_data.get("success") and resp_data.get("data"):
            return resp_data["data"][0]
        raise ToltAPIError("Invalid response from Tolt API")

    async def create_customer(
        self, email: str, partner_id: str, customer_id: str
    ) -> Dict:
        """POST /customers — link a new user to their referrer."""
        data = {"email": email, "partner_id": partner_id, "customer_id": customer_id}
        resp_data = await self._request("POST", "/customers", data)
        if resp_data.get("success") and resp_data.get("data"):
            return resp_data["data"][0]
        raise ToltAPIError("Invalid response from Tolt API")

    async def report_transaction(
        self,
        customer_id: str,
        amount: int,
        charge_id: str,
        billing_type: str = "subscription",
        product_name: str = "Premium Plan",
        interval: Optional[str] = "month",
        source: str = "stripe",
    ) -> Dict:
        """POST /transactions — report a payment and trigger affiliate credit."""
        data = {
            "amount": amount,
            "customer_id": customer_id,
            "billing_type": billing_type,
            "charge_id": charge_id,
            "product_name": product_name,
            "source": source,
        }
        if interval in ("month", "year"):
            data["interval"] = interval

        resp_data = await self._request("POST", "/transactions", data)
        if resp_data.get("success") and resp_data.get("data"):
            txn = resp_data["data"]
            return txn[0] if isinstance(txn, list) else txn
        raise ToltAPIError("Invalid response from Tolt API")


# Module-level singleton
tolt_client = ToltAPIClient()

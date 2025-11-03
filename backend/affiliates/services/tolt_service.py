"""
Tolt API Client - Service layer for Tolt affiliate tracking.

This is similar to creating an Axios/Fetch wrapper in Node.js.
Handles all HTTP communication with Tolt's REST API.
"""

import logging
from typing import Dict, Optional, Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ToltAPIError(Exception):
    """Custom exception for Tolt API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class ToltAPIClient:
    """
    Tolt API Client - handles all communication with Tolt's API.
    
    Like Express/Node.js equivalent:
    ```javascript
    class ToltAPIClient {
        async trackClick(referralCode, pageUrl) { ... }
        async createCustomer(email, partnerId, customerId) { ... }
        async reportTransaction(customerId, amount, chargeId) { ... }
    }
    ```
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Tolt API client.
        
        Args:
            api_key: Tolt API key (defaults to settings.TOLT_API_KEY)
            base_url: Tolt API base URL (defaults to settings.TOLT_API_BASE_URL)
        """
        self.api_key = api_key or settings.TOLT_API_KEY
        self.base_url = base_url or settings.TOLT_API_BASE_URL
        
        if not self.api_key:
            logger.warning("Tolt API key not configured. Set TOLT_API_KEY in environment.")
        
        # Default timeout (like axios timeout)
        self.timeout = 30  # seconds
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.
        
        Returns:
            Dict with Authorization and Content-Type headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """
        Make HTTP request to Tolt API.
        
        This is like axios() in Node.js:
        ```javascript
        const response = await axios.post(url, data, { headers });
        ```
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/clicks')
            data: Request body (JSON)
            params: Query parameters
        
        Returns:
            Tuple of (response_data, status_code)
        
        Raises:
            ToltAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            logger.info(f"[TOLT_API] {method} {endpoint}")
            logger.info(f"[TOLT_API] Request: {data}")
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            response_data = response.json() if response.text else {}
            
            logger.info(f"[TOLT_API] Response [{response.status_code}]: {response_data}")
            
            if response.status_code >= 400:
                error_message = response_data.get("message") or response_data.get("error") or "Unknown error"
                raise ToltAPIError(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=response_data
                )
            
            return response_data, response.status_code
            
        except requests.exceptions.Timeout:
            logger.error(f"[TOLT_API] Timeout after {self.timeout}s")
            raise ToltAPIError("Request to Tolt API timed out")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[TOLT_API] Connection error: {str(e)}")
            raise ToltAPIError("Failed to connect to Tolt API")
        
        except ToltAPIError:
            raise
        
        except Exception as e:
            logger.error(f"[TOLT_API] Unexpected error: {str(e)}")
            raise ToltAPIError(f"Unexpected error: {str(e)}")
    
    # ========================================================================
    # Public API Methods (corresponds to Tolt API endpoints)
    # ========================================================================
    
    def track_click(
        self,
        referral_code: str,
        page_url: str,
        device_type: str = "desktop",
        param_name: str = "via"
    ) -> Dict:
        """
        Track a referral link click and get partner_id.
        
        POST /v1/clicks
        
        This is called when user lands on your site with a referral URL.
        Returns the partner_id (referrer's ID) that you'll use later.
        
        Args:
            referral_code: The referral code from URL (e.g., "ABC123")
            page_url: Full URL where click occurred
            device_type: Device type (desktop, mobile, tablet)
            param_name: URL parameter name (default: "ref")
        
        Returns:
            {
                "partner_id": "part_s7mbzRGn46BhVgNFHD6fDgXW",
                "referral_code": "ABC123",
                ...
            }
        
        Example:
            client = ToltAPIClient()
            result = client.track_click(
                referral_code="ABC123",
                page_url="https://tubegenius.com/signup"
            )
            partner_id = result["partner_id"]
        """
        data = {
            "param": param_name,
            "value": referral_code,
            "page": page_url,
            "device": device_type
        }
        
        response_data, _ = self._make_request("POST", "/clicks", data=data)
        
        if response_data.get("success") and response_data.get("data"):
            click_data = response_data["data"][0]
            return click_data
        else:
            raise ToltAPIError("Invalid response from Tolt API")
    
    def create_customer(
        self,
        email: str,
        partner_id: str,
        customer_id: str
    ) -> Dict:
        """
        Create a customer in Tolt (link user to their referrer).
        
        POST /v1/customers
        
        Call this after user completes signup.
        Establishes the relationship between the new user and their referrer.
        
        Args:
            email: User's email address
            partner_id: Tolt partner ID (from track_click response)
            customer_id: Your internal user ID (Django user.id or user.email)
        
        Returns:
            {
                "customer_id": "cust_dK9bzRGn46BhVgNFHD6fDgXW",  # Tolt's customer ID
                "email": "user@example.com",
                "partner_id": "part_s7mbzRGn46BhVgNFHD6fDgXW",
                ...
            }
        
        Example:
            client = ToltAPIClient()
            result = client.create_customer(
                email="user@example.com",
                partner_id="part_s7mbzRGn46BhVgNFHD6fDgXW",
                customer_id="user_123"  # Your Django user ID
            )
            tolt_customer_id = result["customer_id"]
        """
        data = {
            "email": email,
            "partner_id": partner_id,
            "customer_id": customer_id
        }
        
        response_data, _ = self._make_request("POST", "/customers", data=data)
        
        if response_data.get("success") and response_data.get("data"):
            customer_data = response_data["data"][0]
            return customer_data
        else:
            raise ToltAPIError("Invalid response from Tolt API")
    
    def report_transaction(
        self,
        customer_id: str,
        amount: int,
        charge_id: str,
        billing_type: str = "subscription",
        product_name: str = "Premium Plan",
        interval: Optional[str] = "month",
        source: str = "stripe"
    ) -> Dict:
        """
        Report a transaction to Tolt (triggers affiliate credit).
        
        POST /v1/transactions
        
        Call this after successful payment.
        Tolt will automatically credit the referrer based on your configured rates.
        
        Args:
            customer_id: Tolt customer ID (from create_customer response)
            amount: Amount in cents (e.g., 9999 = $99.99)
            charge_id: Stripe charge/payment intent ID
            billing_type: "subscription" or "one_time"
            product_name: Name of product/plan (can be string or list)
            interval: "month", "year", "week", or None for one-time
            source: Payment processor (default: "stripe")
        
        Returns:
            {
                "id": "txn_evCzwwY3vuKRxx4wGSew5JC3",
                "status": "paid",
                "amount": "4700",
                "charge_id": "ch_9bzRGn46BhVgNFHD6fDgXW",
                "partner_id": "part_Af9JVFe4qNhykiMmvDypzxUk",
                "customer_id": "cus_mLRF6e6qjbiEfkiBBp2Tw2PV",
                "interval": "month",
                "billing_type": "subscription",
                "product_names": ["Basic Monthly"],
                ...
            }
        
        Example:
            client = ToltAPIClient()
            result = client.report_transaction(
                customer_id="cust_dK9bzRGn46BhVgNFHD6fDgXW",
                amount=9999,  # $99.99
                charge_id="ch_stripe123",
                product_name="Pro Plan - Monthly"
            )
        """
        # Tolt expects product_names as array
        product_names = [product_name] if isinstance(product_name, str) else product_name
        
        data = {
            "amount": amount,
            "customer_id": customer_id,
            "billing_type": billing_type,
            "charge_id": charge_id,
            "product_names": product_names,  # Send as array
            "source": source,
        }
        
        # Add interval for subscriptions
        if interval:
            data["interval"] = interval
        
        response_data, _ = self._make_request("POST", "/transactions", data=data)
        
        if response_data.get("success") and response_data.get("data"):
            transaction_data = response_data["data"]
            if isinstance(transaction_data, list):
                transaction_data = transaction_data[0]
            return transaction_data
        else:
            raise ToltAPIError("Invalid response from Tolt API")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def is_enabled(self) -> bool:
        """
        Check if Tolt integration is enabled.
        
        Returns:
            True if Tolt is configured with API key
        """
        return bool(self.api_key)
    
    def health_check(self) -> bool:
        """
        Check if Tolt API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # For now, we'll just check if we have valid credentials
            return self.is_enabled()
        except Exception as e:
            logger.error(f"[TOLT_API] Health check failed: {str(e)}")
            return False


# Singleton instance (like exporting a single axios instance in Node.js)
tolt_client = ToltAPIClient()

import stripe
from django.conf import settings
from djstripe.models import Price, Product
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminPermission


class StripeProductPriceSyncView(APIView):
    """
    Sync local dj-stripe Products and Prices to a NEW Stripe account.

    - Checks by name (Product) and by product+amount+currency (Price).
    - Skips if already exists in the target account.
    - Creates only missing ones.
    """

    permission_classes = [IsAuthenticated, IsAdminPermission]

    @extend_schema(
        summary="Sync Products and Prices to new Stripe account",
        description=(
            "Synchronizes local dj-stripe Products and Prices to a new Stripe account. "
            "This endpoint checks for existing products by name and prices by product, amount, and currency. "
            "Only missing products and prices are created in the target Stripe account. "
            "Existing items are skipped to avoid duplicates."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Sync completed successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Success message",
                            "example": "Product & Price sync complete",
                        },
                        "summary": {
                            "type": "object",
                            "properties": {
                                "created": {
                                    "type": "object",
                                    "properties": {
                                        "products": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of created product names",
                                            "example": ["Basic Plan", "Pro Plan"],
                                        },
                                        "prices": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of created prices with format: product_name - amount currency",
                                            "example": [
                                                "Basic Plan - 9.99 usd",
                                                "Pro Plan - 29.99 usd",
                                            ],
                                        },
                                    },
                                },
                                "skipped": {
                                    "type": "object",
                                    "properties": {
                                        "products": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of skipped product names (already exist)",
                                            "example": ["Enterprise Plan"],
                                        },
                                        "prices": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of skipped prices (already exist)",
                                            "example": ["Enterprise Plan - 99.99 usd"],
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            ),
            500: OpenApiResponse(
                description="Internal server error during sync",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Error message describing what went wrong",
                            "example": "Stripe API error: Invalid API key",
                        }
                    },
                },
            ),
        },
        tags=["Stripe Sync"],
    )
    def post(self, request):
        stripe.api_key = settings.NEW_STRIPE_SECRET_KEY

        results = {
            "created": {"products": [], "prices": []},
            "skipped": {"products": [], "prices": []},
        }

        try:
            # ---------------------------------------
            # 1️⃣ SYNC PRODUCTS
            # ---------------------------------------
            existing_products = {
                p["name"]: p for p in stripe.Product.list(limit=100).auto_paging_iter()
            }

            for product in Product.objects.all():
                if product.name in existing_products:
                    results["skipped"]["products"].append(product.name)
                    continue

                product_data = {
                    "name": product.name,
                    "active": product.active,
                    "metadata": product.metadata or {},
                }
                if product.description:
                    product_data["description"] = product.description

                stripe_product = stripe.Product.create(**product_data)
                results["created"]["products"].append(stripe_product.name)

            # ---------------------------------------
            # 2️⃣ SYNC PRICES
            # ---------------------------------------
            # Fetch all Stripe prices for comparison
            existing_prices = list(stripe.Price.list(limit=100).auto_paging_iter())
            existing_products = list(stripe.Product.list(limit=100).auto_paging_iter())

            for price in Price.objects.all():
                if not price.product:
                    continue

                # Find corresponding product in Stripe (by name)
                product_in_stripe = next(
                    (p for p in existing_products if p.name == price.product.name), None
                )
                if not product_in_stripe:
                    # Product not found, skip this price
                    continue

                # Check if a similar price already exists (same amount + currency + product)
                match = next(
                    (
                        p
                        for p in existing_prices
                        if p.unit_amount == price.unit_amount
                        and p.currency == price.currency
                        and p.product == product_in_stripe.id
                    ),
                    None,
                )

                if match:
                    results["skipped"]["prices"].append(
                        f"{price.product.name} - {price.unit_amount/100} {price.currency}"
                    )
                    continue

                stripe_price = stripe.Price.create(
                    currency=price.currency,
                    unit_amount=price.unit_amount,
                    recurring=price.recurring or None,
                    product=product_in_stripe.id,
                )
                results["created"]["prices"].append(
                    f"{price.product.name} - {stripe_price.unit_amount/100} {stripe_price.currency}"
                )

            return Response(
                {"message": "Product & Price sync complete", "summary": results},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

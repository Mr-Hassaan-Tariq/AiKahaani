"""
Permission classes for the payments app.
"""

import logging

from djstripe.models import Subscription
from rest_framework.permissions import BasePermission
from djstripe.enums import SubscriptionStatus

from .utils import VALID_SUB_STATUSES, get_or_create_customer

logger = logging.getLogger(__name__)


class HasActiveSubscriptionPermission(BasePermission):
    """
    Permission class that only allows access to users with an active subscription.

    This permission checks if the current authenticated user has an active
    subscription using djstripe models. Valid subscription statuses include:
    - active
    - trialing
    - paused (if available)

    Usage:
        permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]
    """

    message = "You must have an active subscription to access this resource."

    def has_permission(self, request, view):
        """
        Check if the user has an active subscription.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user has active subscription, False otherwise
        """
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # Get or create the Stripe customer for this user
            customer = get_or_create_customer(request.user)

            # Check for active subscription
            active_subscription = (
                Subscription.objects.filter(
                    customer=customer, status__in=VALID_SUB_STATUSES
                )
                .order_by("-created")
                .first()
            )

            if active_subscription:
                logger.info(
                    f"User {request.user.email} has active subscription: "
                    f"{active_subscription.id} (status: {active_subscription.status})"
                )
                return True
            else:
                logger.warning(
                    f"User {request.user.email} attempted to access protected resource "
                    f"without active subscription"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error checking subscription for user {request.user.email}: {str(e)}"
            )
            # In case of error, deny access for security
            return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check (same as has_permission for this use case).

        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The object being accessed

        Returns:
            bool: True if user has active subscription, False otherwise
        """
        return self.has_permission(request, view)


class HasPaidSubscriptionPermission(BasePermission):
    """
    Permission that allows access only to users with a paid (non-trial) active subscription.

    Trialing users are denied. This is intended for features not available on free trial.

    Usage:
        permission_classes = [IsAuthenticated, HasPaidSubscriptionPermission]
    """

    message = "Niches are not available on free trial. Please upgrade your plan."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            customer = get_or_create_customer(request.user)
            subscription = (
                Subscription.objects.filter(customer=customer)
                .order_by("-created")
                .first()
            )

            if not subscription:
                return False

            # Deny explicitly if the user is on trial
            if subscription.status == SubscriptionStatus.trialing:
                return False

            # Allow for other valid statuses while excluding trialing
            return subscription.status in VALID_SUB_STATUSES and subscription.status != SubscriptionStatus.trialing

        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

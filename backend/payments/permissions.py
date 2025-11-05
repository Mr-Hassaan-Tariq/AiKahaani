"""
Permission classes for the payments app.
"""

import logging

from django.conf import settings
from djstripe.enums import SubscriptionStatus
from djstripe.models import Subscription
from rest_framework.permissions import BasePermission

from .utils import VALID_SUB_STATUSES, get_or_create_customer

logger = logging.getLogger(__name__)


class HasActiveSubscriptionPermission(BasePermission):
    """
    Permission class that only allows access to users with an active subscription.

    Admin users (superuser or users with admin role) can bypass this check and
    access the resource without a subscription.

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
        Check if the user has an active subscription or is an admin.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user has active subscription or is admin, False otherwise
        """
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow admin users to bypass subscription check
        try:
            if request.user.is_admin() or request.user.is_superuser:
                logger.info(
                    f"Admin user {request.user.email} accessing protected resource "
                    f"without subscription check"
                )
                return True
        except Exception:
            # If is_admin() method doesn't exist or fails, continue with subscription check
            pass

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
            return (
                subscription.status in VALID_SUB_STATUSES
                and subscription.status != SubscriptionStatus.trialing
            )

        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class TrialOutlineLimitPermission(BasePermission):
    """
    Allow trial users to generate outlines up to a limit; paid users unaffected.

    Denies access when the authenticated user's current subscription is trialing
    AND they have already generated 10 or more outlines. Otherwise allows.
    """

    message = "Trial limit reached for outlines on trial. Please upgrade."

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

            # If not on trial, no limit enforced by this permission
            if not subscription or subscription.status != SubscriptionStatus.trialing:
                return True

            # Lazy import to avoid circulars
            from scripts.models import ScriptOutline  # noqa: WPS433

            outlines_count = ScriptOutline.objects.filter(user=request.user).count()
            limit = getattr(settings, "TRIAL_OUTLINE_LIMIT", 10)
            allowed = outlines_count < limit
            if not allowed:
                self.message = f"Trial limit reached: You can generate up to {limit} outlines on trial."
            return allowed

        except Exception:
            # Fail closed for safety
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

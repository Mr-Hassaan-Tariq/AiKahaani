"""
Common mixins for API views.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class GetMethodUserRateThrottle(UserRateThrottle):
    """Throttle class for GET requests by authenticated users."""

    scope = "get"

    def allow_request(self, request, view):
        if request.method != "GET":
            return True
        return super().allow_request(request, view)


class PostMethodUserRateThrottle(UserRateThrottle):
    """Throttle class for POST requests by authenticated users."""

    scope = "post"

    def allow_request(self, request, view):
        if request.method != "POST":
            return True
        return super().allow_request(request, view)


class PutMethodUserRateThrottle(UserRateThrottle):
    """Throttle class for PUT requests by authenticated users."""

    scope = "put"

    def allow_request(self, request, view):
        if request.method != "PUT":
            return True
        return super().allow_request(request, view)


class DeleteMethodUserRateThrottle(UserRateThrottle):
    """Throttle class for DELETE requests by authenticated users."""

    scope = "delete"

    def allow_request(self, request, view):
        if request.method != "DELETE":
            return True
        return super().allow_request(request, view)


class GetMethodAnonRateThrottle(AnonRateThrottle):
    """Throttle class for GET requests by anonymous users."""

    scope = "get"

    def allow_request(self, request, view):
        if request.method != "GET":
            return True
        return super().allow_request(request, view)


class PostMethodAnonRateThrottle(AnonRateThrottle):
    """Throttle class for POST requests by anonymous users."""

    scope = "post"

    def allow_request(self, request, view):
        if request.method != "POST":
            return True
        return super().allow_request(request, view)


class PutMethodAnonRateThrottle(AnonRateThrottle):
    """Throttle class for PUT requests by anonymous users."""

    scope = "put"

    def allow_request(self, request, view):
        if request.method != "PUT":
            return True
        return super().allow_request(request, view)


class DeleteMethodAnonRateThrottle(AnonRateThrottle):
    """Throttle class for DELETE requests by anonymous users."""

    scope = "delete"

    def allow_request(self, request, view):
        if request.method != "DELETE":
            return True
        return super().allow_request(request, view)


class MethodSpecificThrottleMixin:
    """
    Mixin that applies method-specific throttling to views.

    This mixin automatically adds throttle classes for all HTTP methods
    (GET, POST, PUT, DELETE) with different rate limits for authenticated
    and anonymous users based on the settings.py configuration:

    - GET: 3/minute
    - POST: 20/minute
    - PUT: 20/minute
    - DELETE: 10/minute

    Usage:
        class MyView(MethodSpecificThrottleMixin, generics.ListAPIView):
            # Your view implementation
            pass
    """

    throttle_classes = [
        GetMethodUserRateThrottle,
        GetMethodAnonRateThrottle,
        PostMethodUserRateThrottle,
        PostMethodAnonRateThrottle,
        PutMethodUserRateThrottle,
        PutMethodAnonRateThrottle,
        DeleteMethodUserRateThrottle,
        DeleteMethodAnonRateThrottle,
    ]

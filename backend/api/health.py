import os

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Railway
    Returns 200 if all systems are healthy, 503 if any issues
    """
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "checks": {"database": "unknown", "environment": "unknown"},
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check environment variables
    required_vars = [
        "SECRET_KEY",
        "GOOGLE_OAUTH2_CLIENT_ID",
        "GOOGLE_OAUTH2_CLIENT_SECRET",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        health_status["checks"]["environment"] = (
            f"unhealthy: missing {', '.join(missing_vars)}"
        )
        health_status["status"] = "unhealthy"
    else:
        health_status["checks"]["environment"] = "healthy"

    # Set HTTP status code
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JsonResponse(health_status, status=status_code)

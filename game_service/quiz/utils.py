import requests
from django.conf import settings


def report_match_result(user_id, won):
    """Best-effort push of a match result to auth_service's stats endpoint.

    A failure here shouldn't break the game flow for the players, so
    errors are swallowed rather than raised.
    """
    try:
        requests.post(
            f"{settings.AUTH_SERVICE_URL}/api/internal/update-stats/",
            json={"user_id": user_id, "won": won},
            headers={"X-Internal-Key": settings.INTERNAL_API_KEY},
            timeout=3,
        )
    except requests.RequestException:
        pass

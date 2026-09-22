import time

import jwt
from django.conf import settings


def issue_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_EXP_SECONDS,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

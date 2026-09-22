import jwt
from django.conf import settings
from rest_framework import authentication, exceptions


class JWTUser:
    """Stand-in for a Django user, built entirely from a verified JWT.

    game_service has no local user table; player identity comes from the
    token auth_service issued at login, not from a database lookup here.
    """

    def __init__(self, user_id, username):
        self.id = user_id
        self.user_id = user_id
        self.username = username
        self.is_authenticated = True


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        return (JWTUser(payload["user_id"], payload["username"]), None)

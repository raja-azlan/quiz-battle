from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .jwt_utils import issue_token
from .models import Profile
from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    token = issue_token(user)
    return Response({"token": token, "user_id": user.id, "username": user.username})


@api_view(["GET"])
@permission_classes([AllowAny])
def profile(request, user_id):
    try:
        profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(ProfileSerializer(profile).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_stats(request):
    """Internal endpoint: game_service calls this after a match ends."""
    if request.headers.get("X-Internal-Key") != settings.INTERNAL_API_KEY:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get("user_id")
    won = bool(request.data.get("won"))

    try:
        profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    profile.games_played += 1
    if won:
        profile.wins += 1
    else:
        profile.losses += 1
    profile.save()

    return Response(ProfileSerializer(profile).data)

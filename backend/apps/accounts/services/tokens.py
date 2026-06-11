"""JWT token service."""

from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


@dataclass(frozen=True)
class TokenPair:
    """JWT access and refresh token pair."""

    access: str
    refresh: str


class TokenService:
    """Issue, refresh, and blacklist JWT tokens."""

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate credentials and return the user."""
        user = authenticate(username=email, password=password)
        if user is None:
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("User account is inactive.")
        return user

    def issue_pair(self, user: User) -> TokenPair:
        """Issue a new refresh/access token pair."""
        refresh = RefreshToken.for_user(user)
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    def refresh_access(self, refresh_token: str) -> TokenPair:
        """Rotate a refresh token and return a fresh pair."""
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)
            refresh.blacklist()
        except (TokenError, KeyError, ObjectDoesNotExist) as exc:
            raise ValueError("Invalid refresh token.") from exc
        new_refresh = RefreshToken.for_user(user)
        return TokenPair(access=str(new_refresh.access_token), refresh=str(new_refresh))

    def blacklist(self, refresh_token: str) -> None:
        """Blacklist a refresh token."""
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError as exc:
            raise ValueError("Invalid refresh token.") from exc

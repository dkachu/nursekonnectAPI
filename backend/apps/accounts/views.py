"""Authentication API views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import (
    LoginSerializer,
    LogoutSerializer,
    OTPResendSerializer,
    OTPVerifySerializer,
    RefreshSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.accounts.services.registration import RegistrationInput, RegistrationService
from apps.accounts.services.tokens import TokenService
from apps.accounts.services.verification import OTPService


class RegisterView(APIView):
    """Register patients and nurses."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Create a user and role-specific profile."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = RegistrationService().register(
                RegistrationInput(
                    email=data["email"],
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone_number=data["phone_number"],
                    role=data["role"],
                )
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and issue JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Return access and refresh tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_service = TokenService()
        try:
            user = token_service.authenticate(**serializer.validated_data)
        except ValueError as exc:
            raise AuthenticationFailed(str(exc)) from exc
        tokens = token_service.issue_pair(user)
        return Response(
            {
                "access": tokens.access,
                "refresh": tokens.refresh,
                "user": UserSerializer(user).data,
            }
        )


class RefreshView(APIView):
    """Rotate a refresh token and return new tokens."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Refresh JWT credentials."""
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tokens = TokenService().refresh_access(serializer.validated_data["refresh"])
        except ValueError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        return Response({"access": tokens.access, "refresh": tokens.refresh})


class LogoutView(APIView):
    """Blacklist a refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Logout the current user by blacklisting their refresh token."""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            TokenService().blacklist(serializer.validated_data["refresh"])
        except ValueError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyOTPView(APIView):
    """Verify an email or phone OTP."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Verify the authenticated user's OTP."""
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = OTPService().verify_otp(
                user=request.user,
                purpose=serializer.validated_data["purpose"],
                code=serializer.validated_data["code"],
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response({"user": UserSerializer(user).data})


class ResendOTPView(APIView):
    """Create a replacement OTP for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Resend an OTP for email or phone verification."""
        serializer = OTPResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = OTPService().resend_otp(
                user=request.user,
                purpose=serializer.validated_data["purpose"],
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response({"expires_at": result.expires_at})


class VerifyEmailView(VerifyOTPView):
    """Verify email using an OTP."""


class VerifyPhoneView(VerifyOTPView):
    """Verify phone using an OTP."""

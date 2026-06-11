"""Authentication API views."""

from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.serializers import (
    LoginSerializer,
    OTPResendSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.accounts.services.registration import RegistrationInput, RegistrationService
from apps.accounts.services.tokens import TokenService
from apps.accounts.services.verification import OTPService
from apps.audit_logs.services.audit import AuditLogService


def request_ip(request: Request) -> str | None:
    """Return the best-effort client IP address."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def refresh_cookie_kwargs() -> dict[str, object]:
    """Return secure refresh-cookie settings."""
    return {
        "httponly": True,
        "secure": settings.AUTH_REFRESH_COOKIE_SECURE,
        "samesite": settings.AUTH_REFRESH_COOKIE_SAMESITE,
        "path": settings.AUTH_REFRESH_COOKIE_PATH,
        "max_age": int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    }


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Store refresh token in an HttpOnly cookie."""
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        **refresh_cookie_kwargs(),
    )


def clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh-token cookie."""
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )


def refresh_token_from_request(request: Request) -> str | None:
    """Read refresh token from secure cookie, with body fallback for API clients."""
    body_token = request.data.get("refresh") if isinstance(request.data, dict) else None
    if body_token:
        return str(body_token)
    return request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)


class RegisterView(APIView):
    """Register patients and nurses."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

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
        AuditLogService().record(
            actor=user,
            action="AUTH_REGISTERED",
            resource="User",
            resource_id=user.id,
            ip_address=request_ip(request),
            metadata={"role": user.role},
        )
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and issue JWT tokens."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request: Request) -> Response:
        """Return access token and set refresh token in an HttpOnly cookie."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_service = TokenService()
        try:
            user = token_service.authenticate(**serializer.validated_data)
        except ValueError as exc:
            AuditLogService().record(
                actor=None,
                action="AUTH_LOGIN_FAILED",
                resource="User",
                resource_id="authentication",
                ip_address=request_ip(request),
                metadata={"email": serializer.validated_data["email"]},
            )
            raise AuthenticationFailed(str(exc)) from exc
        tokens = token_service.issue_pair(user)
        AuditLogService().record(
            actor=user,
            action="AUTH_LOGIN_SUCCEEDED",
            resource="User",
            resource_id=user.id,
            ip_address=request_ip(request),
        )
        response = Response({"access": tokens.access, "user": UserSerializer(user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class RefreshView(APIView):
    """Rotate a refresh token from cookie or body and return a new access token."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"

    def post(self, request: Request) -> Response:
        """Refresh JWT credentials."""
        refresh_token = refresh_token_from_request(request)
        if not refresh_token:
            raise ValidationError({"refresh": "Refresh token is required."})
        try:
            tokens = TokenService().refresh_access(refresh_token)
        except ValueError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        response = Response({"access": tokens.access})
        set_refresh_cookie(response, tokens.refresh)
        return response


class LogoutView(APIView):
    """Blacklist a refresh token."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_logout"

    def post(self, request: Request) -> Response:
        """Logout the current user by blacklisting their refresh token."""
        refresh_token = refresh_token_from_request(request)
        try:
            if refresh_token:
                TokenService().blacklist(refresh_token)
        except ValueError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        AuditLogService().record(
            actor=request.user,
            action="AUTH_LOGGED_OUT",
            resource="User",
            resource_id=request.user.id,
            ip_address=request_ip(request),
        )
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class CurrentUserView(APIView):
    """Return the authenticated user's context for session restoration."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return current user and non-medical profile metadata."""
        return Response({"user": UserSerializer(request.user).data})


class VerifyOTPView(APIView):
    """Verify an email or phone OTP."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

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
        AuditLogService().record(
            actor=request.user,
            action="AUTH_OTP_VERIFIED",
            resource="User",
            resource_id=request.user.id,
            ip_address=request_ip(request),
            metadata={"purpose": serializer.validated_data["purpose"]},
        )
        return Response({"user": UserSerializer(user).data})


class ResendOTPView(APIView):
    """Create a replacement OTP for the authenticated user."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_resend"

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
        AuditLogService().record(
            actor=request.user,
            action="AUTH_OTP_RESENT",
            resource="User",
            resource_id=request.user.id,
            ip_address=request_ip(request),
            metadata={"purpose": serializer.validated_data["purpose"]},
        )
        return Response({"expires_at": result.expires_at})


class VerifyEmailView(VerifyOTPView):
    """Verify email using an OTP."""


class VerifyPhoneView(VerifyOTPView):
    """Verify phone using an OTP."""

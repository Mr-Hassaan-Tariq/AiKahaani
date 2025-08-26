import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import MagicLinkToken
from .serializers import (
    GoogleAuthInputSerializer,
    MagicLinkLoginSerializer,
    MagicLinkLoginSuccessResponseSerializer,
    MagicLinkVerifySerializer,
    MagicLinkVerifySuccessResponseSerializer,
    UserSerializer,
    UserSignupSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()


class SignupView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignupSerializer

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response(
                {"message": "User created successfully", "user": user_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginAPIView(APIView):
    """
    POST /api/auth/google/
    - Expects a Google Authorization Code or ID token.
    - Returns an access token, refresh token, and user details.

    Example body:
    {
        "id_token": "<google_authorization_code_or_id_token>"
    }

    Example response:
    {
        "access": "<access_token>",
        "refresh": "<refresh_token>",
        "user": {
            "id": "<user_id>",
            "email": "<user_email>",
            "fullname": "<user_fullname>",
            "username": "<user_username>"
        },
        "created": "<boolean>"
    }
    """

    authentication_classes = []  # Allow anonymous access
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthInputSerializer

    def post(self, request):
        """
        Authenticates the user using a Google ID token or authorization code.
        """
        s = GoogleAuthInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        token = s.validated_data["id_token"]

        CLIENT_ID = settings.GOOGLE_OAUTH2_CLIENT_ID
        CLIENT_SECRET = settings.GOOGLE_OAUTH2_CLIENT_SECRET

        if not CLIENT_ID or not CLIENT_SECRET:
            return Response(
                {
                    "detail": "Authentication service temporarily unavailable(MAY BE MISSED CREDENTIALS?)"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Handle both Authorization Code and ID Token scenarios
            if token.startswith("4/"):
                logger.info("Processing Google authorization code")
                id_token = self.exchange_authorization_code(token)
            else:
                logger.info("Processing Google ID token")
                id_token = token

            idinfo = self.verify_id_token(id_token)

            if not idinfo.get("email_verified", False):
                logger.warning(
                    f"Email not verified for user: {idinfo.get('email', 'unknown')}"
                )
                return Response(
                    {"detail": "Email not verified by Google."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, created = self.get_or_create_user(idinfo)
            refresh = RefreshToken.for_user(user)

            data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.pk),
                    "email": user.email,
                    "fullname": user.fullname,
                    "username": user.username,
                },
                "created": created,
            }

            logger.info(f"Successful Google authentication for user: {user.email}")
            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response(
                {"detail": f"Authentication service temporarily unavailable: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError:
            return Response(
                {"detail": "Invalid authentication credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def exchange_authorization_code(self, auth_code):
        """
        Exchanges the authorization code for an ID token.
        """
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:3000/",  # TODO: CHANGE THIS TO THE PRODUCTION/STAGING URL
        }

        try:
            response = requests.post(token_url, data=token_data, timeout=30)
            response.raise_for_status()
            token_info = response.json()

            if "id_token" not in token_info:
                logger.error("No ID token received from Google OAuth exchange")
                raise ValueError("No ID token received from Google")

            logger.info("Successfully exchanged authorization code for ID token")
            return token_info.get("id_token")

        except requests.RequestException as e:
            logger.error(f"Failed to exchange authorization code: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise e

    def verify_id_token(self, id_token):
        """
        Verifies the Google ID token and returns the user information.
        """
        try:
            user_info = google_id_token.verify_oauth2_token(
                id_token, google_requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            logger.info(
                f"Successfully verified Google ID token for user: {user_info.get('email', 'unknown')}"
            )
            return user_info
        except Exception as e:
            logger.error(f"Failed to verify Google ID token: {str(e)}")
            raise ValueError("Invalid Google ID token") from e

    def get_or_create_user(self, idinfo):
        """
        Retrieves or creates a user based on the ID token information.
        """
        email = idinfo["email"]
        defaults = {
            "fullname": f"{idinfo.get('given_name', '')} {idinfo.get('family_name', '')}".strip()[
                :150
            ]
        }

        user, created = User.objects.get_or_create(
            email=email, username=email.strip("@")[0], defaults=defaults
        )

        if created:
            logger.info(f"Created new user: {email}")
        else:
            logger.info(f"Retrieved existing user: {email}")

        return user, created


class MagicLinkLoginAPIView(APIView):
    """
    API endpoint for sending magic link to user's email for passwordless authentication.

    If user doesn't exist, a new user will be created with the provided email.
    The username will be extracted from the part before '@' in the email.
    """

    permission_classes = [AllowAny]
    serializer_class = MagicLinkLoginSerializer

    @extend_schema(
        operation_id="magic_link_login",
        summary="Send Magic Link for Authentication",
        description=(
            "Sends a magic link to the provided email address for passwordless authentication. "
            "If the user doesn't exist, a new user account will be created automatically. "
            "The username is extracted from the email address (part before '@'). "
            "The magic link expires in 15 minutes."
        ),
        request=MagicLinkLoginSerializer,
        examples=[
            OpenApiExample(
                "Magic Link Request",
                summary="Request magic link for existing or new user",
                description="Send magic link to user's email",
                value={"email": "john.doe@example.com"},
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=MagicLinkLoginSuccessResponseSerializer,
                description="Magic link sent successfully",
                examples=[
                    OpenApiExample(
                        "Magic Link Sent",
                        value={"message": "Magic link sent to your email"},
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid email format or missing email",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"email": ["Enter a valid email address."]},
                        response_only=True,
                    )
                ],
            ),
            500: OpenApiResponse(
                description="Email service is temporarily unavailable",
                examples=[
                    OpenApiExample(
                        "Email Service Error",
                        value={"error": "Failed to send magic link email"},
                        response_only=True,
                    )
                ],
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        username = email.split("@")[0]

        # Get or create user if doesn't exist
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": username}
        )
        token = MagicLinkToken.objects.create(
            user=user, expires_at=timezone.now() + timedelta(minutes=15)
        )
        magic_link = f"{settings.FRONTEND_URL}/magic-link?token={token.token}"

        # Send magic link email using Anymail
        try:
            send_mail(
                "Your Magic Link",
                f"Click this link to log in: {magic_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response(
                {"message": "Magic link sent to your email"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to send magic link email to {email}: {str(e)}")
            return Response(
                {"error": "Failed to send magic link email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MagicLinkVerifyAPIView(APIView):
    """
    API endpoint for verifying magic link tokens and authenticating users.

    Validates the magic link token and returns JWT authentication tokens.
    The token is single-use and gets invalidated after successful verification.
    """

    permission_classes = [AllowAny]
    serializer_class = MagicLinkVerifySerializer

    @extend_schema(
        operation_id="magic_link_verify",
        summary="Verify Magic Link Token",
        description=(
            "Verifies the magic link token received via email and returns JWT authentication tokens. "
            "The token is validated for existence and expiration. Upon successful verification, "
            "the token is immediately invalidated (single-use) and JWT tokens are generated for the user."
        ),
        request=MagicLinkVerifySerializer,
        examples=[
            OpenApiExample(
                "Magic Link Verification Request",
                summary="Verify magic link token",
                description="Submit the token received via magic link email",
                value={"token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=MagicLinkVerifySuccessResponseSerializer,
                description="Token verified and JWT tokens generated",
                examples=[
                    OpenApiExample(
                        "Authentication Success",
                        value={
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNjg5ODA2MSwidXNlcl9pZCI6MX0.abc123def456",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA2ODExNjYxLCJ1c2VyX2lkIjoxfQ.xyz789uvw456",
                            "user": {
                                "id": "1",
                                "email": "john.doe@example.com",
                                "username": "john.doe",
                                "fullname": "John Doe",
                            },
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid, expired or malformed token",
                examples=[
                    OpenApiExample(
                        "Invalid Token",
                        value={"detail": "Invalid or expired magic link."},
                        response_only=True,
                    )
                ],
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            link_token = MagicLinkToken.objects.get(
                token=token, expires_at__gt=timezone.now()
            )
            user = link_token.user
            link_token.delete()  # Invalidate the used token

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": str(user.pk),
                        "email": user.email,
                        "username": user.username,
                        "fullname": user.fullname,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except MagicLinkToken.DoesNotExist:
            logger.warning(f"Invalid or expired magic link token attempted: {token}")
            return Response(
                {"detail": "Invalid or expired magic link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

import logging
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.mixins import MethodSpecificThrottleMixin

from .models import BlacklistedAccessToken, EmailVerificationToken, MagicLinkToken
from .serializers import (
    GoogleAuthInputSerializer,
    LogoutSerializer,
    MagicLinkLoginSerializer,
    MagicLinkLoginSuccessResponseSerializer,
    MagicLinkVerifySerializer,
    MagicLinkVerifySuccessResponseSerializer,
    MessageResponseSerializer,
    ProfilePictureUploadSerializer,
    UserDetailsUpdateSerializer,
    UserSerializer,
    UserSignupSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()


class SignupView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignupSerializer

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user, context={"request": request}).data
            return Response(
                {"message": "User created successfully", "user": user_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginAPIView(MethodSpecificThrottleMixin, APIView):
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
            "redirect_uri": f"{settings.FRONTEND_URL}/",  # TODO: CHANGE THIS TO THE PRODUCTION/STAGING URL
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
            email=email, username=email.split("@")[0], defaults=defaults
        )

        if created:
            logger.info(f"Created new user: {email}")
        else:
            logger.info(f"Retrieved existing user: {email}")

        return user, created


class MagicLinkLoginAPIView(MethodSpecificThrottleMixin, APIView):
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

        # Send magic link email using template
        try:
            # Prepare context for template
            context = {
                "user_name": user.fullname or user.username,
                "magic_link": magic_link,
            }

            # Choose template based on whether user is new or existing
            if created:
                # New user signup
                html_message = render_to_string("mails/magic_link_signup.html", context)
                plain_message = render_to_string("mails/magic_link_signup.txt", context)
            else:
                # Existing user login
                html_message = render_to_string("mails/magic_link_login.html", context)
                plain_message = render_to_string("mails/magic_link_login.txt", context)

            send_mail(
                "👉 Your TubeGenius Access Link",
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
                html_message=html_message,
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


class UserDetailsUpdateAPIView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="user_details_update",
        summary="Update current user's details",
        description=(
            "Authenticated endpoint to update the signed-in user's profile fields. "
            "Allows updating fullName, username, emailAddress, preferredLanguage."
        ),
        request=UserDetailsUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="User details updated successfully",
                response=UserSerializer,
                examples=[
                    OpenApiExample(
                        "Update Success",
                        value={
                            "id": "1",
                            "email": "jane.doe@example.com",
                            "username": "jane.doe",
                            "fullname": "Jane Doe",
                            "preferred_language": "en",
                            "profile_picture": "https://example.com/profile.jpg",
                            "is_email_verified": False,
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        "Username Taken",
                        value={"username": ["This username is already taken."]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Invalid Email",
                        value={"emailAddress": ["Enter a valid email address."]},
                        response_only=True,
                    ),
                ],
            ),
        },
        tags=["Users"],
    )
    def put(self, request):
        serializer = UserDetailsUpdateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        previous_email = user.email
        email_in_payload = serializer.validated_data.get("emailAddress")

        serializer.update_user(user)
        # breakpoint()
        # If email was updated, send verification link
        if email_in_payload and email_in_payload != previous_email:
            try:
                # Invalidate any previous verification tokens for this user
                EmailVerificationToken.objects.filter(user=user).delete()

                token_obj = EmailVerificationToken.objects.create(
                    user=user,
                    email=user.email,
                    expires_at=timezone.now() + timedelta(hours=24),
                )
                verify_url = f"{settings.FRONTEND_URL}/email-verification?token={token_obj.token}"

                send_mail(
                    "Verify your email address",
                    f"Click this link to verify your email: {verify_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send email verification to {user.email}: {str(e)}"
                )
                return Response(
                    {"error": "Failed to send verification email"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="user_details_get",
        summary="Get current user's details",
        description=(
            "Authenticated endpoint to fetch the signed-in user's profile details."
        ),
        responses={200: UserSerializer},
        tags=["Users"],
    )
    def get(self, request):
        user = request.user
        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class EmailVerificationAPIView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="verify_email",
        summary="Verify email change",
        description=(
            "Verifies a user's email address using a one-time token. "
            "Marks the user's email as verified upon success."
        ),
        responses={
            200: OpenApiResponse(
                description="Email verified successfully",
                response=UserSerializer,
            ),
            400: OpenApiResponse(
                description="Invalid or expired verification token",
            ),
        },
        tags=["Users"],
    )
    def get(self, request, token):
        try:
            vtoken = EmailVerificationToken.objects.get(
                token=token, expires_at__gt=timezone.now()
            )
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = vtoken.user
        # Optionally ensure the verified email matches the pending email
        if user.email != vtoken.email:
            user.email = vtoken.email
        user.is_email_verified = True
        user.save()

        vtoken.delete()
        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class MagicLinkVerifyAPIView(MethodSpecificThrottleMixin, APIView):
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


class LogoutAPIView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        operation_id="logout",
        summary="Logout user",
        description=(
            "Logs out the current user by blacklisting both refresh and access tokens. "
            "Requires a valid refresh token in the request body."
        ),
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(
                response=MessageResponseSerializer,
                description="Logout successful",
                examples=[
                    OpenApiExample(
                        "Logout Success",
                        value={"message": "Logged out successfully"},
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid refresh token",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"refresh": ["Refresh token is required."]},
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
        refresh_token = serializer.validated_data["refresh"]
        access_token = request.auth
        try:
            access_token_obj = access_token

            # Store access token JTI in our custom blacklist with its expiry
            access_jti = access_token_obj.get("jti")
            access_exp = access_token_obj.get("exp")
            if access_jti and access_exp:
                expires_at = datetime.fromtimestamp(int(access_exp), tz=dt_timezone.utc)
                BlacklistedAccessToken.objects.get_or_create(
                    jti=access_jti,
                    defaults={
                        "user": request.user,
                        "expires_at": expires_at,
                    },
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class UserProfilePictureAPIView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        operation_id="user_profile_picture_update",
        summary="Update current user's profile picture",
        description=(
            "Authenticated endpoint to upload or replace the signed-in user's profile picture. "
            "Accepts multipart/form-data with field 'profile_picture'."
        ),
        request=ProfilePictureUploadSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile picture updated successfully",
                response=UserSerializer,
            ),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Users"],
    )
    def patch(self, request):
        serializer = ProfilePictureUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_image = serializer.validated_data["profile_picture"]

        try:
            user.profile_picture.delete(save=False)
        except Exception:
            pass

        user.profile_picture = new_image
        user.save()
        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="user_profile_picture_delete",
        summary="Delete current user's profile picture",
        description=(
            "Authenticated endpoint to remove the signed-in user's profile picture. "
            "If no picture exists, the operation is a no-op."
        ),
        responses={
            200: OpenApiResponse(
                description="Profile picture deleted successfully",
                response=UserSerializer,
            )
        },
        tags=["Users"],
    )
    def delete(self, request):
        user = request.user
        try:
            user.profile_picture.delete(save=False)
        except Exception:
            pass
        user.profile_picture = None
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

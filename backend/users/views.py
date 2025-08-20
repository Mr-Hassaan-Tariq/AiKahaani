import logging
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import GoogleAuthInputSerializer, UserSerializer, UserSignupSerializer

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
            "fullname": "<user_fullname>"
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
                {"detail": "Authentication service temporarily unavailable"},
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
                logger.warning(f"Email not verified for user: {idinfo.get('email', 'unknown')}")
                return Response({"detail": "Email not verified by Google."}, status=status.HTTP_400_BAD_REQUEST)

            user = self.get_or_create_user(idinfo)
            refresh = RefreshToken.for_user(user)

            data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.pk),
                    "email": user.email,
                    "fullname": user.fullname,
                },
                "created": created,
            }

            logger.info(f"Successful Google authentication for user: {user.email}")
            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException:
            return Response(
                {"detail": "Authentication service temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError:
            return Response(
                {"detail": "Invalid authentication credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception:
            return Response(
                {"detail": "Authentication service temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
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
            "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
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
            raise

    def verify_id_token(self, id_token):
        """
        Verifies the Google ID token and returns the user information.
        """
        try:
            user_info = google_id_token.verify_oauth2_token(
                id_token, google_requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            logger.info(f"Successfully verified Google ID token for user: {user_info.get('email', 'unknown')}")
            return user_info
        except Exception as e:
            logger.error(f"Failed to verify Google ID token: {str(e)}")
            raise ValueError("Invalid Google ID token")

    def get_or_create_user(self, idinfo):
        """
        Retrieves or creates a user based on the ID token information.
        """
        email = idinfo["email"]
        defaults = {
            "fullname": f"{idinfo.get('given_name', '')} {idinfo.get('family_name', '')}".strip()[:150]
        }
        
        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        
        if created:
            logger.info(f"Created new user: {email}")
        else:
            logger.info(f"Retrieved existing user: {email}")
            
        return user

from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from users.models import BlacklistedAccessToken


class JWTAuthenticationWithAccessTokenBlacklist(JWTAuthentication):
    """
    Extends SimpleJWT's JWTAuthentication to also reject access tokens whose
    JTIs are stored in our BlacklistedAccessToken table. This provides
    immediate invalidation of access tokens upon logout.
    """

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)

        # Only apply additional blacklist check for access tokens
        token_type = str(token.get("token_type", ""))
        if token_type == "access":
            jti = token.get("jti")
            if jti:
                # If a matching JTI exists and not yet expired, reject
                now = timezone.now()
                is_blacklisted = BlacklistedAccessToken.objects.filter(
                    jti=jti, expires_at__gt=now
                ).exists()
                if is_blacklisted:
                    raise InvalidToken("Token is blacklisted")

            # Opportunistic cleanup of expired blacklist entries (about 2% of requests)
            # if random.random() < 0.02:
            #     BlacklistedAccessToken.objects.filter(expires_at__lte=timezone.now()).delete()

        return token

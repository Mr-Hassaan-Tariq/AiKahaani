from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class JWTAuthenticationWithAccessTokenBlacklistExtension(
    OpenApiAuthenticationExtension
):
    """
    OpenAPI extension for JWTAuthenticationWithAccessTokenBlacklist
    """

    target_class = "users.authentication.JWTAuthenticationWithAccessTokenBlacklist"
    name = "JWT Authentication"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization", token_prefix="Bearer", bearer_format="JWT"
        )

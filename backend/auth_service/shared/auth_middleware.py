from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        try:
            validated_token = self.jwt_auth.get_validated_token(
                self.jwt_auth.get_raw_token(
                    self.jwt_auth.get_header(request)
                )
            )
            request.user = self.jwt_auth.get_user(validated_token)
            request.token = validated_token
        except (InvalidToken, AuthenticationFailed):
            pass

        response = self.get_response(request)
        return response

# authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        token = request.COOKIES.get("access_token")

        if token is None:
            return None

        validated_token = self.get_validated_token(token)
        print(self.get_user(validated_token),validated_token)
        return self.get_user(validated_token), validated_token
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import Application


class FTLOAuth2Authentication(OAuth2Authentication):
    """
    The default OAuth2Authentication class doesn't associate the token to the user associated to the application.
    Custom Authentication class to support having client_credentials token associated to the user.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication is not None and self.is_client_credential_request(authentication):
            access_token = authentication[1]
            user = access_token.application.user
            return user, access_token
        else:
            return authentication

    def is_client_credential_request(self, authentication):
        access_token = authentication[1]
        return access_token.application.authorization_grant_type == Application.GRANT_CLIENT_CREDENTIALS

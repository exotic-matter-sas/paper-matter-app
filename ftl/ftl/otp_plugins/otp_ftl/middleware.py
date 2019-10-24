from rest_framework.authentication import SessionAuthentication


class FTLSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        response = super().authenticate(request)

        if response and response[0] and response[0].is_verified():
            return response
        else:
            return None

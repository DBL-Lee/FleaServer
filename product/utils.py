from serializers import UserSerializer
from rest_framework_jwt.settings import api_settings

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token' : token,
        'user' : UserSerializer(user).data,
        'expiration' : api_settings.JWT_EXPIRATION_DELTA.days*24*3600+api_settings.JWT_EXPIRATION_DELTA.seconds}

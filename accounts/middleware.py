import logging
from django.http import JsonResponse
from accounts.utils import validate_jwt_token, encode_decode_jwt_token, is_api_open
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from e_commerce.constants import (
    UNAUTHORISED_ACCESS,
    ENCODE,
    DECODE,
    INVALID_TOKEN,
    USER_DOSENT_EXISTS,
)
from accounts.models import MyUser


class AuthenticationAuthorisationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_valid = False
        self.jwt = False

    def __call__(self, request):
        try:
            if not is_api_open(request):
                try:
                    token = request.META.get("HTTP_AUTHORIZATION", None)
                    if token is not None:
                        is_valid = validate_jwt_token(token)
                        if is_valid:
                            token_data = encode_decode_jwt_token(
                                token, convertion_type=DECODE
                            )
                            user_query = MyUser.objects.filter(user_id=token_data["id"])
                            if user_query:
                                response = self.get_response(request)
                                return response
                        else:
                            response = {
                                "status": HTTP_404_NOT_FOUND,
                                "error": USER_DOSENT_EXISTS,
                            }
                            return JsonResponse(response)
                    else:
                        return JsonResponse(
                            {"msg": INVALID_TOKEN, "status": HTTP_401_UNAUTHORIZED}
                        )
                except Exception as er:
                    return JsonResponse(
                        {"msg": INVALID_TOKEN, "status": HTTP_401_UNAUTHORIZED}
                    )
            else:
                request.session.flush()
                response = self.get_response(request)
                return response
        except Exception as error:
            logging.exception(error)
            return JsonResponse(
                {"status": HTTP_401_UNAUTHORIZED, "error": UNAUTHORISED_ACCESS}
            )

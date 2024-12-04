import logging

from django.http import JsonResponse
from e_commerce import constants as EcommerceConstants
from rest_framework import status

from accounts import utils as AccountsUtils
from accounts.models import MyUser
from utilities.classes import ErrorResponse


class AuthenticationAuthorisationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_valid = False
        self.jwt = False

    def __call__(self, request):
        try:
            if not AccountsUtils.is_api_open(request):
                try:
                    token = request.META.get("HTTP_AUTHORIZATION", None)
                    if token is not None:
                        is_valid = AccountsUtils.validate_jwt_token(token)
                        if is_valid:
                            token_data = AccountsUtils.encode_decode_jwt_token(
                                token, convertion_type=EcommerceConstants.DECODE
                            )
                            user_query = MyUser.objects.filter(user_id=token_data["id"])
                            if user_query:
                                response = self.get_response(request)
                                return response
                        else:
                            return JsonResponse(
                                ErrorResponse(EcommerceConstants.USER_DOSENT_EXISTS),
                                status=status.HTTP_404_NOT_FOUND,
                            )
                    else:
                        return JsonResponse(
                            ErrorResponse(EcommerceConstants.INVALID_TOKEN),
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                except Exception as er:
                    return JsonResponse(
                        ErrorResponse(EcommerceConstants.INVALID_TOKEN),
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                request.session.flush()
                response = self.get_response(request)
                return response
        except Exception as error:
            logging.exception(error)
            return JsonResponse(
                ErrorResponse(EcommerceConstants.UNAUTHORISED_ACCESS),
                status=status.HTTP_401_UNAUTHORIZED,
            )

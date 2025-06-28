import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from accounts import utils as AccountsUtils
from accounts.models import MyUser, UserSession
from e_commerce import constants as EcommerceConstants
from utils import dbops as DBOps
from utils.classes import ErrorResponse


class AuthenticationAuthorisationMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_valid = False
        self.jwt = False

    def __call__(self, request):
        try:
            if request.path.startswith("/admin") or request.path.startswith(
                settings.STATIC_URL
            ):
                return self.get_response(request)
            if not AccountsUtils.is_api_open(request):
                try:
                    token = request.META.get("HTTP_AUTHORIZATION", None)
                    if token is None:
                        return JsonResponse(
                            ErrorResponse(EcommerceConstants.INVALID_TOKEN),
                            status=status.HTTP_401_UNAUTHORIZED,
                        )

                    is_valid = AccountsUtils.validate_jwt_token(token)
                    if not is_valid:
                        return JsonResponse(
                            ErrorResponse(EcommerceConstants.USER_DOSENT_EXISTS),
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    token_data = AccountsUtils.encode_decode_jwt_token(
                        token, convertion_type=EcommerceConstants.DECODE
                    )
                    user_id = token_data.get("user_id")

                    (session_status, session_obj) = DBOps.get_record(
                        UserSession,
                        {
                            "session_id": token_data.get("session_id"),
                            "user_id": user_id,
                            "is_active": True,
                        },
                    )

                    if not session_status:
                        return JsonResponse(
                            ErrorResponse(EcommerceConstants.INVALID_TOKEN),
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                    session_obj.save(update_fields=["last_active"])

                    (user_status, user_query) = DBOps.get_record(
                        MyUser, {"user_id": user_id}
                    )
                    if not user_status:
                        return JsonResponse(
                            ErrorResponse(EcommerceConstants.USER_DOSENT_EXISTS),
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    request.user = user_query
                    return self.get_response(request)
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

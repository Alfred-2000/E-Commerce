import enum

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status
from rest_framework.response import Response

from accounts import utils as AccountsUtils
from e_commerce import constants as EcommerceConstants


class ResponseMessages:
    def success_response(
        self, msg: str, data: dict = None, status: status = None, headers: dict = None
    ) -> dict:
        """
        Function returns a success response with a custom message.

        Args:
            msg : The success message to be included in the response.
            data : Additional data to include in the response.

        Returns:
            response : A dictionary containing the success message.
        """
        response = {"message": msg}
        if data:
            response.update(data)
        if headers:
            return Response(response, status=status, headers=headers)
        return Response(response, status=status)

    def error_response(self, error: str = None, status: status = None) -> dict:
        """
        Function returns an error response with a custom error message.

        Args:
            error : The error message to be included in the response.

        Returns:
            response : A dictionary containing the error message.
        """
        response = {}
        if error:
            response.update({"error": error})
        return Response(response, status=status)


responseMessage = ResponseMessages()
SuccessResponse = responseMessage.success_response
ErrorResponse = responseMessage.error_response


class StrEnum(str, enum.Enum):
    def _generate_next_value_(name, *_):
        return name


class LowercaseStrEnum(StrEnum):
    def _generate_next_value_(name, *_):
        return name.lower()


class UppercasesStrEnum(StrEnum):
    def _generate_next_value_(name, *_):
        return name.upper()


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an optional `remove_fields` argument
    to exclude certain fields dynamically.
    """

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop("remove_fields", None)
        super().__init__(*args, **kwargs)
        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name, None)


class HttpMethod(LowercaseStrEnum):
    GET = enum.auto()
    POST = enum.auto()
    PUT = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()


class FilterSearchOrderingMixin:
    """
    Mixin to enable filter, search, and ordering backends.
    Each ViewSet can optionally define:
        - filterset_class
        - search_fields
        - ordering_fields
        - ordering (optional default ordering)
    """

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]


class GetUserFromTokenMixin:
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request_method: str = request.method
        token = request.META.get("HTTP_AUTHORIZATION", None)
        token_data = AccountsUtils.encode_decode_jwt_token(
            token, convertion_type=EcommerceConstants.DECODE
        )
        user_id = token_data.get("user_id")
        user_name = request.user.username
        if request.content_type == "application/json":
            request.data["user"] = user_id
        else:
            kwargs["user"] = user_id

        if request_method.lower() in [HttpMethod.POST]:
            request.data["created_by"] = user_name
        elif request_method.lower() in [HttpMethod.PATCH]:
            request.data["updated_by"] = user_name

        return request

import enum


class ResponseMessages:
    def success_response(self, msg: str, data: dict = None) -> dict:
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
        return response

    def error_response(self, error: str) -> dict:
        """
        Function returns an error response with a custom error message.

        Args:
            error : The error message to be included in the response.

        Returns:
            response : A dictionary containing the error message.
        """
        response = {"error": error}
        return response


responseMessage = ResponseMessages()
SuccessResponse = responseMessage.success_response
ErrorResponse = responseMessage.error_response


class StrEnum(str, enum.Enum):
    def _generate_next_value_(name, *_):
        return name


class LowercaseStrEnum(StrEnum):
    def _generate_next_value_(name, *_):
        return name.lower()


class HttpMethod(LowercaseStrEnum):
    GET = enum.auto()
    POST = enum.auto()
    PUT = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()

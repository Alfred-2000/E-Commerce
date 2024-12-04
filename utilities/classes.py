from enum import Enum, auto


class LowercaseStrEnum(Enum):
    def __str__(self):
        # Return the string representation of the enum in lowercase
        return self.name.lower()


class LookupExpression(LowercaseStrEnum):
    CONTAINS = auto()
    ICONTAINS = auto()
    NOTCONTAINS = auto()
    NOTICONTAINS = auto()
    CONTAINSIN = auto()
    ICONTAINSIN = auto()
    NOTCONTAINSIN = auto()
    NOTICONTAINSIN = auto()
    EXACT = auto()
    IN = auto()
    RANGE = auto()
    LT = auto()
    LTE = auto()
    GTE = auto()
    GT = auto()
    NOTIN = auto()
    NOTRANGE = auto()


class DataTypes(LowercaseStrEnum):
    """
    A simple enum representing all the
    commonly used python data types as
    lower case string
    """

    BYTES = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    DATE = auto()
    TIME = auto()
    TIMESTAMP = auto()
    TIMEDELTA = auto()
    FILE = auto()
    UUID = auto()


class ResponseMessages:
    def success_response(self, msg: str, data: dict = None) -> dict:
        """
        Function returns a success response with a custom message.

        Input:
            msg : The success message to be included in the response.
            data : Additional data to include in the response.

        Output:
            response : A dictionary containing the success message.
        """
        response = {"message": msg}
        if data:
            response.update(data)
        return response

    def error_response(self, error: str) -> dict:
        """
        Function returns an error response with a custom error message.

        Input:
            error : The error message to be included in the response.

        Output:
            response : A dictionary containing the error message.
        """
        response = {"error": error}
        return response


responseMessage = ResponseMessages()
SuccessResponse = responseMessage.success_response
ErrorResponse = responseMessage.error_response

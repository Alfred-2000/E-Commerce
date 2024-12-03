import hashlib
import logging
from datetime import datetime
from typing import Union

import jwt
import pytz
from django.urls import resolve
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from utilities import filtersets as UtilitiesFilters

from accounts import constants as AccountsConstants
from accounts.models import MyUser


def get_current_timestamp_of_timezone(time_zone: str) -> int:
    """
    Function to get current timestamp for the given timezone

    Input:
        time_zone : A string representing the timezone

    Output:
        timestamp_value : The current timestamp for the given timezone.
    """
    timezone = pytz.timezone(time_zone)
    timestamp_value = round(datetime.now(timezone).timestamp())
    return timestamp_value


def hash_given_password(password):
    password_hash_key = password
    output = hashlib.md5(password_hash_key.encode()).hexdigest()
    return output


def get_redis_datas(key: str, fields: list) -> dict:
    """
    Retrieves specific fields from a Redis hash and returns them as a dictionary.

    Input:
        key : The Redis hash key to retrieve the data from.
        fields : A list of field names to retrieve from the Redis hash.

    Output:
        return_data: A dictionary where keys are the field names from 'fields' and values are the decoded
              Redis values. If no data is found, an empty dictionary is returned.
    """
    return_data = dict()
    redis_data = EcommerceSettings.REDIS_CONNECTION_READ.hmget(str(key), fields)
    if redis_data:
        redis_data = [i.decode("utf-8") if i else "" for i in redis_data]
        if redis_data:
            return_data = dict(zip(fields, redis_data))
            return return_data
        else:
            logging.error("KEY_VALUE_NOT_FOUND_IN_REDIS :" + "{}".format(key))
    return return_data


def user_key_redis(data: dict) -> str:
    """
    Generate a Redis key based on the provided user data.

    Input:
        data : A dictionary containing user details.

    Output:
        redis_key: redis key generated by combining the 'username' and 'user_id' with an underscore.
    """
    redis_key = data["username"] + "_" + str(data["user_id"])
    return redis_key


def encode_decode_jwt_token(
    data_to_convert: dict, convertion_type: str
) -> Union[str, dict]:
    """
    Encode or decode a JWT token based on the specified conversion type.

    Input:
        data_to_convert : The data to be encoded or decoded.
        conversion_type : The type of conversion. Should be either 'encode' or 'decode'.

    Output:
        response: The result of the conversion. If encoding, returns the JWT token as a string.
                          If decoding, returns the decoded payload as a dictionary.
    """
    if convertion_type == EcommerceConstants.ENCODE:
        try:
            response = jwt.encode(
                payload=data_to_convert,
                key=EcommerceConstants.JWT_SECRECT_KEY,
                algorithm="HS256",
            )
        except Exception as e:
            logging.error(e)
            response = ""
    if convertion_type == EcommerceConstants.DECODE:
        try:
            response = jwt.decode(
                jwt=data_to_convert,
                key=EcommerceConstants.JWT_SECRECT_KEY,
                algorithms=["HS256"],
            )
        except Exception as e:
            logging.error(e)
            response = {}
    return response


def validate_jwt_token(token: str) -> bool:
    """
    Validates a given JWT token by decoding it and checking the existence of the associated user.

    Input:
    token : The JWT token to be validated.

    Output:
    token_status : True if the token is valid (i.e., the user exists in the database), False otherwise.
    """
    token_status = False
    try:
        user_details = encode_decode_jwt_token(
            token, convertion_type=EcommerceConstants.DECODE
        )
        if user_details:
            user_query = MyUser.objects.filter(user_id=user_details["id"])
            token_status = True if user_query else False
        return token_status
    except Exception as error:
        logging.error("Exception occured while validating jwt token {}".format(error))
        return token_status


def is_api_open(request: Request) -> bool:
    """
    Function checks if the given API endpoint (URL path) is considered "open" by verifying
    its URL name against a predefined list of open APIs.

    Input:
        request : The HTTP request object, which contains the URL path to be resolved and checked.

    Output:
        api_status : True if the API endpoint is in the OPEN_API list, False otherwise.
    """
    api_status = False
    try:
        if EcommerceSettings.OPEN_API.get(resolve(request.path).url_name):
            api_status = True
            return api_status
    except Exception as er:
        return api_status


def check_feature_permission(token: str) -> bool:
    """
    Function checks if the user associated with the given JWT token has permission for a feature
    based on the user's "is_superuser" status.

    Input:
        token (str): The JWT token to be checked for permissions.

    Output:
        token_status: True if the user is a superuser, False otherwise.
    """
    token_data = encode_decode_jwt_token(
        token, convertion_type=EcommerceConstants.DECODE
    )
    token_status = True if token_data["is_superuser"] else False
    return token_status


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Custom authentication class that disables CSRF protection for session authentication.
    """

    def enforce_csrf(self, request: Request):
        """
        Override the enforce_csrf method to disable CSRF verification for session-based authentication.

        Input:
            request: The incoming HTTP request object.

        Output:
            None
        """
        return


class UsersListingFilterSet(UtilitiesFilters.GenericModelFilterSet):
    class Meta:
        model = MyUser
        fields = AccountsConstants.USERS_META_FIELDS

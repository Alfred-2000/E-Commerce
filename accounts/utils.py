import pytz
import hashlib
import logging
import jwt
from datetime import datetime
from e_commerce.settings import (
    REDIS_CONNECTION_READ,
    OPEN_API,
)
from e_commerce.constants import (
    JWT_SECRECT_KEY,
    ENCODE,
    DECODE,
)
from accounts.models import MyUser
from django.urls import resolve
from rest_framework.authentication import SessionAuthentication


def get_current_timestamp_of_timezone(time_zone):
    """get current timestamp of given timezone"""
    timezone = pytz.timezone(time_zone)
    return round(datetime.now(timezone).timestamp())


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
    redis_data = REDIS_CONNECTION_READ.hmget(str(key), fields)
    if redis_data:
        redis_data = [i.decode("utf-8") if i else "" for i in redis_data]
        if redis_data:
            return_data = dict(zip(fields, redis_data))
            return return_data
        else:
            logging.error("KEY_VALUE_NOT_FOUND_IN_REDIS :" + "{}".format(key))
    return return_data


def user_key_redis(data: dict) -> str:
    redis_key = data["username"] + "_" + str(data["user_id"])
    return redis_key


def encode_decode_jwt_token(data_to_convert: dict, convertion_type: str) -> dict:
    if convertion_type == ENCODE:
        try:
            response = jwt.encode(
                payload=data_to_convert, key=JWT_SECRECT_KEY, algorithm="HS256"
            )
        except Exception as e:
            logging.error(e)
            response = ""
    if convertion_type == DECODE:
        try:
            response = jwt.decode(
                jwt=data_to_convert, key=JWT_SECRECT_KEY, algorithms=["HS256"]
            )
        except Exception as e:
            logging.error(e)
            response = {}
    return response


def validate_jwt_token(token: str) -> bool:
    try:
        user_details = encode_decode_jwt_token(token, convertion_type=DECODE)
        if user_details:
            user_query = MyUser.objects.filter(user_id=user_details["id"])
            token_status = True if user_query else False
            return token_status
        return False
    except Exception as error:
        logging.error("Exception occured while validating jwt token {}".format(error))
        return False


def is_api_open(request):
    try:
        if OPEN_API.get(resolve(request.path).url_name):
            return True
    except Exception as er:
        return False


def check_feature_permission(token: str) -> bool:
    token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
    return True if token_data["is_superuser"] else False


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

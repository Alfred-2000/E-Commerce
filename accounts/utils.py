
import pytz, hashlib, logging, jwt
from datetime import datetime
from e_commerce.settings import (
    REDIS_CONNECTION_READ,
    OPEN_API,
    MEDIA_URL,
)
from e_commerce.constants import(
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

def get_redis_datas(key, fields):
    redis_data = REDIS_CONNECTION_READ.hmget(str(key),fields)
    if redis_data:
        redis_data = [i.decode('utf-8') if i else '' for i in redis_data]
        if redis_data:
            return dict(zip(fields,redis_data))
        else:
            logging.error("KEY_VALUE_NOT_FOUND_IN_REDIS :" + "{}".format(key))
    return dict()

def user_key_redis(data):
    redis_key = data['username'] + '_' + str(data['user_id'])
    return redis_key

def encode_decode_jwt_token(data_to_convert, convertion_type):
    if convertion_type == ENCODE:
        try:
            response = jwt.encode(payload = data_to_convert, key = JWT_SECRECT_KEY, algorithm = "HS256")
        except Exception as e:
            logging.error(e)
            response = ""
    if convertion_type == DECODE:
        try:
            response = jwt.decode(jwt = data_to_convert, key = JWT_SECRECT_KEY, algorithms = ["HS256"])
        except Exception as e:
            logging.error(e)
            response = {}
    return response

def validate_jwt_token(token):
    try:
        user_details = encode_decode_jwt_token(token, convertion_type=DECODE)
        if user_details:
            user_query = MyUser.objects.filter(user_id = user_details['id'])
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
    except:
        return False
    
def check_feature_permission(token):
    token_data = encode_decode_jwt_token(token, convertion_type=DECODE)
    return True if token_data['is_superuser'] else False

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
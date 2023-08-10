import pytz
import logging
from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN
)
from accounts.models import User
from e_commerce.constants import (
    USER_DOSENT_EXISTS,
    USER_REGISTERED_SUCCESSFULLY,
    USER_LOGGED_IN_SUCCESSFULLY,
    INVALID_CREDENTIALS,
    USER_DELETED_SUCCESSFULLY,
    ENCODE,
    DECODE
)
from e_commerce.settings import (
    TIME_ZONE, REDIS_CONNECTION_WRITE,
)
from accounts.serializers import UserSerializer
from accounts.utils import (
    get_current_timestamp_of_timezone, 
    hash_given_password,
    get_redis_datas,
    user_key_redis,
    encode_decode_jwt_token,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate


class LoginView(APIView):
    def post(self, request):
        try:
            user_query = User.objects.filter(username = request.data['username'])
            if not user_query.exists():
                return Response({"status": HTTP_404_NOT_FOUND, "message": USER_DOSENT_EXISTS, "data": []})
        
            user_object = user_query.get(username = request.data['username'])
            user_data = UserSerializer(user_object).data
            redis_user_key = user_key_redis(user_data)
            test = get_redis_datas(redis_user_key, ['id', 'username', 'password', 'email'])
            admin_token_details = {
                'id' : test.get('id'),
                'username': request.data['username'],
                'email': test.get('email')
            }
            access_token = encode_decode_jwt_token(admin_token_details, convertion_type=ENCODE)
            request_password = hash_given_password(request.data["username"], request.data["password"])
            
            if request_password == test.get('password'):
                response = {"status": HTTP_200_OK, "message": USER_LOGGED_IN_SUCCESSFULLY, "data": []}
                logging.info(response)
                return Response(response, headers = {"Authorization": access_token})
            else:
                response = {"status": HTTP_401_UNAUTHORIZED, "error": INVALID_CREDENTIALS, "data": None}
                logging.info(response)
                return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)


class ListCreateDeleteUser(APIView):

    def post(self, request):
        try:
            request.data['password'] = hash_given_password(request.data['username'], request.data['password'])
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['date_joined'] = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            serializer = UserSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                redis_user_key = user_key_redis(serializer.data)
                REDIS_CONNECTION_WRITE.hmset(redis_user_key, serializer.data)
                response = {"status": HTTP_201_CREATED, "message": USER_REGISTERED_SUCCESSFULLY, "data": serializer.data}
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                logging.info(response)
                return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)


    def delete(self, request, **kwargs):
        try:
            user_query = User.objects.filter(id=kwargs['user_id'])
            user_object = user_query.get(id=kwargs['user_id'])
            user_data = UserSerializer(user_object).data
            redis_user_key = user_key_redis(user_data)
            REDIS_CONNECTION_WRITE.delete(redis_user_key)
            user_object.delete()
            response = {"status": HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY, "data": None}
            logging.info(response)
            return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

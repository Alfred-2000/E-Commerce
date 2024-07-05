import pytz, uuid, logging
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import(
    ListCreateAPIView, ListAPIView,
    CreateAPIView
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN
)
from accounts.models import Myuser
from e_commerce.constants import (
    USER_DOSENT_EXISTS,
    USER_REGISTERED_SUCCESSFULLY,
    USER_LOGGED_IN_SUCCESSFULLY,
    INVALID_CREDENTIALS,
    USER_DELETED_SUCCESSFULLY,
    ENCODE,
    DECODE,
    UNAUTHORISED_ACCESS,
    ACCOUNT_RETRIEVED_SUCCESSFULLY,
    USER_UPDATED_SUCCESSFULLY,
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
    check_feature_permission,
    CsrfExemptSessionAuthentication,
)

class LoginView(APIView):
    def post(self, request):
        try:
            userExist = Myuser.objects.filter(Q(username=request.data['username'])|Q(email=request.data['username']))
            if userExist.exists():
                user_object = userExist.get()
            else:
                return Response({"status": HTTP_404_NOT_FOUND, "message": USER_DOSENT_EXISTS, "data": []})
            user_data = UserSerializer(user_object).data
            redis_user_key = user_key_redis(user_data)
            redis_user_data = get_redis_datas(redis_user_key, ['user_id', 'username', 'password', 'email'])
            user_details = redis_user_data if redis_user_data.get('username') else user_data
            request_password = hash_given_password(request.data["password"])
            if request_password == user_details.get('password'):
                admin_token_details = {
                    'id' : user_details.get('user_id'),
                    'username': request.data['username'],
                    'email': user_details.get('email'),
                    'is_superuser': user_data['is_superuser']
                }
                access_token = encode_decode_jwt_token(admin_token_details, convertion_type=ENCODE)
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

class RegisterUser(CreateAPIView):        
    def post(self, request):
        try:
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data.update({'password': hash_given_password(request.data['password']),
                                 'created_at': datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S"),
                                 'user_id': uuid.uuid4()})
            serializer = UserSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                serializer_data = serializer.data
                serializer_data['is_superuser'] = str(serializer_data['is_superuser'])
                redis_user_key = user_key_redis(serializer_data)
                serializer_data = {k:v for k, v in serializer_data.items() if v != None}
                REDIS_CONNECTION_WRITE.hmset(redis_user_key, serializer_data)
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

class ListDeleteUsers(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not check_feature_permission(token):
            response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
            logging.info(response)
            return Response(response)        
        query_dict = {}
        queryset  = Myuser.objects.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result
    
    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            if not check_feature_permission(token):
                response = {"status": HTTP_400_BAD_REQUEST, "error": UNAUTHORISED_ACCESS, "data": None}
                logging.info(response)
                return Response(response)

            deleted_users = []
            users_list = Myuser.objects.filter(user_id__in = request.data['user_ids'])
            for user_object in users_list:
                user_data = UserSerializer(user_object).data
                deleted_users.append(user_data)
                redis_user_key = user_key_redis(user_data)
                REDIS_CONNECTION_WRITE.delete(redis_user_key)
                user_object.delete()
            response = {"status": HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY, "data": deleted_users}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

class RetrieveUpdateDeleteUser(ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, **kwargs):
        try:
            user_id = str(kwargs['user_id'])
            user_query = Myuser.objects.filter(user_id= user_id)
            user_object = user_query.get()
            user_data = UserSerializer(user_object).data
            response = {"status": HTTP_200_OK, "message": ACCOUNT_RETRIEVED_SUCCESSFULLY, "data": user_data}
            logging.info(response)
            return Response(response)        
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)

    def patch(self, request, **kwargs):
        try:
            user_id = str(kwargs['user_id'])
            user_query = Myuser.objects.filter(user_id = user_id)
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['updated_at'] = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            user_object = user_query.get()
            serializer = UserSerializer(user_object, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_200_OK, "message": USER_UPDATED_SUCCESSFULLY, "data": serializer.data}
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
            user_id = str(kwargs['user_id'])
            user_query = Myuser.objects.filter(user_id=user_id)
            user_object = user_query.get()
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


import uuid
from datetime import datetime

import pytz
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import constants as AccountsConstants
from accounts import utils as AccountsUtils
from accounts.models import MyUser
from accounts.serializers import UserSerializer


class LoginView(APIView):
    def post(self, request):
        try:
            userExist = MyUser.objects.filter(
                Q(username=request.data["username"]) | Q(email=request.data["username"])
            )
            if userExist.exists():
                user_object = userExist.get()
            else:
                return Response(
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": EcommerceConstants.USER_DOSENT_EXISTS,
                    }
                )
            user = authenticate(
                username=request.data["username"], password=request.data["password"]
            )
            if user is not None:
                user_data = UserSerializer(user_object).data
                redis_user_key = AccountsUtils.user_key_redis(user_data)
                redis_user_data = AccountsUtils.get_redis_datas(
                    redis_user_key, ["user_id", "username", "password", "email"]
                )
                user_details = (
                    redis_user_data if redis_user_data.get("username") else user_data
                )
                admin_token_details = {
                    "id": user_details.get("user_id"),
                    "username": request.data["username"],
                    "email": user_details.get("email"),
                    "is_superuser": user_data["is_superuser"],
                }
                access_token = AccountsUtils.encode_decode_jwt_token(
                    admin_token_details, convertion_type=EcommerceConstants.ENCODE
                )
                response = {
                    "message": EcommerceConstants.USER_LOGGED_IN_SUCCESSFULLY,
                }
                return Response(
                    response,
                    status=status.HTTP_200_OK,
                    headers={"Authorization": access_token},
                )
            else:
                response = {
                    "error": EcommerceConstants.INVALID_CREDENTIALS,
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class RegisterUser(generics.CreateAPIView):
    def post(self, request):
        try:
            for field, message in AccountsConstants.USER_FIELD_VALIDATION.items():
                if MyUser.objects.filter(**{field: request.data[field]}).exists():
                    return Response(
                        {"error": message}, status=status.HTTP_400_BAD_REQUEST
                    )

            current_time = AccountsUtils.get_current_timestamp_of_timezone(
                EcommerceSettings.TIME_ZONE
            )
            request.data.update(
                {
                    "password": make_password(request.data["password"]),
                    "created_at": datetime.fromtimestamp(
                        current_time, pytz.timezone(EcommerceSettings.TIME_ZONE)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "user_id": uuid.uuid4(),
                }
            )
            serializer = UserSerializer(
                data=request.data,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer_data = serializer.data
            serializer_data.update(
                {
                    key: int(serializer_data[key])
                    for key in ["is_superuser", "is_staff", "is_active"]
                }
            )
            redis_user_key = AccountsUtils.user_key_redis(serializer_data)
            serializer_data = {k: v for k, v in serializer_data.items() if v != None}
            EcommerceSettings.REDIS_CONNECTION_WRITE.hmset(
                redis_user_key, serializer_data
            )
            response = {
                "user_id": serializer_data["user_id"],
                "message": EcommerceConstants.USER_REGISTERED_SUCCESSFULLY,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({"error": error}, status.HTTP_400_BAD_REQUEST)


class ListDeleteUsers(generics.ListCreateAPIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = MyUser.objects.all().order_by("-updated_at")
    serializer_class = UserSerializer
    filterset_class = AccountsUtils.UsersListingFilterSet

    def list(self, request):
        token = request.META.get("HTTP_AUTHORIZATION", None)
        if not AccountsUtils.check_feature_permission(token):
            response = {"error": EcommerceConstants.UNAUTHORISED_ACCESS}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        query_dict = {}
        queryset = self.queryset.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True, context={"request": request})
            result = self.get_paginated_response(serializer.data)
            return result

    def delete(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", None)
            if not AccountsUtils.check_feature_permission(token):
                response = {"error": EcommerceConstants.UNAUTHORISED_ACCESS}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            deleted_users = []
            users_list = MyUser.objects.filter(user_id__in=request.data["user_ids"])
            for user_object in users_list:
                user_data = UserSerializer(user_object).data
                deleted_users.append(user_data)
                redis_user_key = AccountsUtils.user_key_redis(user_data)
                EcommerceSettings.REDIS_CONNECTION_WRITE.delete(redis_user_key)
                user_object.delete()
            response = {"message": EcommerceConstants.USER_DELETED_SUCCESSFULLY}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeleteUser(generics.ListCreateAPIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)

    def get(self, request, **kwargs):
        try:
            user_id = str(kwargs["user_id"])
            user_query = MyUser.objects.filter(user_id=user_id)
            user_object = user_query.get()
            user_data = UserSerializer(user_object).data
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, **kwargs):
        try:
            user_id = str(kwargs["user_id"])
            user_query = MyUser.objects.filter(user_id=user_id)
            if request.data.get("password"):
                request.data["password"] = make_password(request.data["password"])
            current_time = AccountsUtils.get_current_timestamp_of_timezone(
                EcommerceSettings.TIME_ZONE
            )
            request.data["updated_at"] = datetime.fromtimestamp(
                current_time, pytz.timezone(EcommerceSettings.TIME_ZONE)
            ).strftime("%Y-%m-%d %H:%M:%S")
            user_object = user_query.get()
            serializer = UserSerializer(
                user_object,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
                response = {"message": EcommerceConstants.USER_UPDATED_SUCCESSFULLY}
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {"error": serializer.errors}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        try:
            user_id = str(kwargs["user_id"])
            user_query = MyUser.objects.filter(user_id=user_id)
            user_object = user_query.get()
            user_data = UserSerializer(user_object).data
            redis_user_key = AccountsUtils.user_key_redis(user_data)
            EcommerceSettings.REDIS_CONNECTION_WRITE.delete(redis_user_key)
            user_object.delete()
            response = {"message": EcommerceConstants.USER_DELETED_SUCCESSFULLY}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

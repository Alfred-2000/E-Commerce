import uuid
from datetime import datetime

import pytz
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db.models import Q
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from rest_framework import generics, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from accounts import constants as AccountsConstants
from accounts import utils as AccountsUtils
from accounts.models import MyUser
from accounts.serializers import UserSerializer
from utilities.classes import SuccessResponse, ErrorResponse
from utilities.permissions import required_superuser_access


class LoginView(APIView):
    def post(self, request):
        try:
            try:
                user_object = MyUser.objects.get(
                    Q(username=request.data["username"])
                    | Q(email=request.data["username"])
                )
            except MyUser.DoesNotExist:
                return Response(
                    ErrorResponse(EcommerceConstants.USER_DOSENT_EXISTS),
                    status=status.HTTP_404_NOT_FOUND,
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
                return Response(
                    SuccessResponse(EcommerceConstants.USER_LOGGED_IN_SUCCESSFULLY),
                    status=status.HTTP_200_OK,
                    headers={"Authorization": access_token},
                )
            else:
                return Response(
                    ErrorResponse(EcommerceConstants.INVALID_CREDENTIALS),
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class RegisterUser(generics.CreateAPIView):
    def post(self, request):
        try:
            user_details: dict = request.data
            for field, message in AccountsConstants.USER_FIELD_VALIDATION.items():
                if MyUser.objects.filter(**{field: user_details[field]}).exists():
                    return Response(
                        ErrorResponse(message), status=status.HTTP_400_BAD_REQUEST
                    )

            User = get_user_model()
            user_details.update({"user_id": uuid.uuid4()})
            User.objects.create_user(**user_details)
            user_query = MyUser.objects.get(username=user_details["username"])
            serializer_data = UserSerializer(user_query).data
            AccountsUtils.set_user_info_to_redis(serializer_data)
            response_data = {"user_id": serializer_data["user_id"]}
            return Response(
                SuccessResponse(
                    EcommerceConstants.USER_REGISTERED_SUCCESSFULLY, data=response_data
                ),
                status=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status.HTTP_400_BAD_REQUEST)


class UserManagementViewSet(viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    queryset = MyUser.objects.order_by("-updated_at", "-created_at")
    serializer_class = UserSerializer
    filterset_class = AccountsUtils.UsersListingFilterSet
    search_fields = AccountsConstants.USERS_SEARCH_AND_FILTER_FIELDS

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_superuser:
    #         return self.queryset
    #     else:
    #         return self.queryset.exclude(is_superuser=True)

    @required_superuser_access
    def list(self, request, *args, **kwargs):
        """
        Override the list method to check for superuser access before retrieving a user.
        If the logged-in user is a superuser, allow access to any user; otherwise, allow access
        only to non-superusers.
        """
        return super().list(request, *args, **kwargs)

    @required_superuser_access
    def put(self, request):
        """
        Override the destroy method to check for superuser access before deleting a user.
        Superusers can delete any user, while non-superusers can only delete their own user.
        """
        try:
            deleted_users = []
            users_list = MyUser.objects.filter(user_id__in=request.data["user_ids"])
            for user_object in users_list:
                user_data = UserSerializer(user_object).data
                deleted_users.append(user_data)
                redis_user_key = AccountsUtils.user_key_redis(user_data)
                user_object.delete()
                EcommerceSettings.REDIS_CONNECTION_WRITE.delete(redis_user_key)
            return Response(
                SuccessResponse(EcommerceConstants.USER_DELETED_SUCCESSFULLY),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)

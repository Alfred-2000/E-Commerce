import uuid

from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import decorators, generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import constants as AccountsConstants
from accounts import models as AccountsModels
from accounts import serializers as AccountsSerializer
from accounts import utils as AccountsUtils
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from utils import dbops as DBOps
from utils.classes import (
    ErrorResponse,
    FilterSearchOrderingMixin,
    HttpMethod,
    SuccessResponse,
)
from utils.permissions import IsObjectOwnerOrSuperUserPermission, IsSuperUserPermission

User = get_user_model()


class LoginView(APIView):
    def post(self, request):
        try:
            user_name = request.data["username"]
            password = request.data["password"]
            try:
                user_object = AccountsModels.MyUser.objects.get(
                    Q(username=user_name) | Q(email=user_name)
                )
            except AccountsModels.MyUser.DoesNotExist:
                return Response(
                    ErrorResponse(EcommerceConstants.USER_DOSENT_EXISTS),
                    status=status.HTTP_404_NOT_FOUND,
                )

            user = authenticate(username=user_name, password=password)
            if not user:
                return Response(
                    ErrorResponse(EcommerceConstants.INVALID_CREDENTIALS),
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = AccountsSerializer.UserSerializer(user_object).data
            redis_user_key = AccountsUtils.user_key_redis(user_data)
            redis_user_data = AccountsUtils.get_redis_datas(
                redis_user_key, ["user_id", "username", "password", "email"]
            )
            user_details = (
                redis_user_data if redis_user_data.get("username") else user_data
            )
            session_id = str(uuid.uuid4())
            (status_obj, _) = DBOps.create_record(
                AccountsModels.UserSession,
                {
                    "session_id": session_id,
                    "user": user,
                    "ip_address": request.META.get("REMOTE_ADDR"),
                    "device": request.META.get("HTTP_USER_AGENT"),
                    "is_active": True,
                },
            )
            if not status_obj:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            admin_token_details = {
                "user_id": user_details.get("user_id"),
                "session_id": session_id,
                "username": user_name,
                "email": user_details.get("email"),
                "is_superuser": user_data["is_superuser"],
            }
            access_token = AccountsUtils.encode_decode_jwt_token(
                admin_token_details, convertion_type=EcommerceConstants.ENCODE
            )
            return Response(
                SuccessResponse(
                    EcommerceConstants.USER_LOGGED_IN_SUCCESSFULLY,
                    data={"user_id": user_details.get("user_id")},
                ),
                status=status.HTTP_200_OK,
                headers={"Authorization": access_token},
            )

        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)

    def post(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", None)
            token_data = AccountsUtils.encode_decode_jwt_token(
                token, convertion_type=EcommerceConstants.DECODE
            )
            user_id = token_data.get("user_id")
            session_id = token_data.get("session_id")

            (status_obj, session_obj) = DBOps.get_record(
                AccountsModels.UserSession,
                {"session_id": session_id, "user_id": user_id, "is_active": True},
            )

            if not status_obj:
                return Response(
                    ErrorResponse(EcommerceConstants.SESSION_NOT_FOUND),
                    status=status.HTTP_404_NOT_FOUND,
                )

            session_obj.is_active = False
            session_obj.save(update_fields=["is_active"])

            return Response(
                SuccessResponse(EcommerceConstants.USER_LOGGED_OUT_SUCCESSFULLY),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class RegisterUser(generics.CreateAPIView):
    def validate_unique_fields(self, request_data: dict) -> None:
        for field, message in AccountsConstants.USER_FIELD_VALIDATION.items():
            if AccountsModels.MyUser.objects.filter(
                **{field: request_data[field]}
            ).exists():
                raise ValueError(message)

    def post(self, request) -> Response:
        try:
            request_data: dict = request.data
            self.validate_unique_fields(request_data)
            User.objects.create_user(**request_data)
            user_query = AccountsModels.MyUser.objects.get(
                username=request_data["username"]
            )
            serializer_data = AccountsSerializer.UserSerializer(user_query).data
            AccountsUtils.set_user_info_to_redis(serializer_data)
            response_data = {"user_id": serializer_data["user_id"]}
            return Response(
                SuccessResponse(
                    EcommerceConstants.USER_REGISTERED_SUCCESSFULLY, data=response_data
                ),
                status=status.HTTP_201_CREATED,
            )
        except ValueError as val_err:
            return Response(
                ErrorResponse(str(val_err)), status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return Response(ErrorResponse(error), status.HTTP_400_BAD_REQUEST)


class UserManagementViewSet(FilterSearchOrderingMixin, viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    permission_classes = [IsSuperUserPermission]
    queryset = AccountsModels.MyUser.objects.order_by("-updated_at", "-created_at")
    serializer_class = AccountsSerializer.UserSerializer
    filterset_class = AccountsUtils.UsersListingFilterSet
    search_fields = AccountsConstants.USERS_SEARCH_AND_FILTER_FIELDS

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request):
        """
        Override the destroy method to check for superuser access before deleting a user.
        Superusers can delete any user, while non-superusers can only delete their own user.
        """
        try:
            deleted_users = []
            users_list = AccountsModels.MyUser.objects.filter(
                user_id__in=request.data["user_ids"]
            )
            for user_object in users_list:
                user_data = AccountsSerializer.UserSerializer(user_object).data
                deleted_users.append(user_data)
                redis_user_key = AccountsUtils.user_key_redis(user_data)
                user_object.delete()
                EcommerceSettings.REDIS_CONNECTION_WRITE.delete(redis_user_key)
            return Response(
                SuccessResponse(EcommerceConstants.USER_DELETED_SUCCESSFULLY),
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class UserAddressViewset(viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    permission_classes = [IsObjectOwnerOrSuperUserPermission]
    serializer_class = AccountsSerializer.AddressSerializer
    queryset = AccountsModels.Address.objects.order_by("-updated_at", "-created_at")

    def get_queryset(self):
        user_obj = self.request.user
        if not user_obj:
            queryset = self.queryset.none()
        elif user_obj.is_superuser:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            request_data: dict = request.data
            user_id = request_data["user"]
            if request_data.get("is_default"):
                AccountsModels.Address.objects.filter(user=user_id).update(
                    is_default=False, updated_by=user_id
                )
            request_data["created_by"] = request.user.user_id
            serializer = AccountsSerializer.AddressSerializer(data=request_data)
            if not serializer.is_valid():
                return Response(
                    ErrorResponse(serializer.errors), status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(
                SuccessResponse(
                    EcommerceConstants.ADDRESS_CREATED_SUCCESSFULLY,
                    data=serializer.data,
                ),
                status=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return Response(
                ErrorResponse(str(error)), status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            request_data: dict = request.data
            user_id = request_data["user"]
            if request_data.get("is_default"):
                AccountsModels.Address.objects.filter(user=user_id).update(
                    is_default=False, updated_by=user_id
                )
            request_data["updated_by"] = request.user.user_id
            serializer = AccountsSerializer.AddressSerializer(
                instance, data=request_data, partial=True
            )
            if not serializer.is_valid():
                return Response(
                    ErrorResponse(serializer.errors), status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(
                SuccessResponse(
                    EcommerceConstants.ADDRESS_UPDATED_SUCCESSFULLY,
                    data=serializer.data,
                ),
                status=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return Response(
                ErrorResponse(str(error)), status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            address = self.get_object()
            address.delete()
            return Response(
                SuccessResponse(
                    EcommerceConstants.ADDRESS_DELETED_SUCCESSFULLY,
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                ErrorResponse(str(error)), status=status.HTTP_400_BAD_REQUEST
            )

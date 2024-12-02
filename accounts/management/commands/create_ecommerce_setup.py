import logging
import uuid
from django.http import HttpRequest
from django.core.management import BaseCommand
from datetime import datetime
from e_commerce import constants as EcommerceConstants
from accounts.models import MyUser
from accounts import utils as AccountsUtils
from e_commerce.settings import TIME_ZONE, REDIS_CONNECTION_WRITE
from accounts.serializers import UserSerializer
from django.core.management import call_command
from system.models import SystemConfig
from system.serializers import SystemconfigSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "This management command is used for creating Super user and debug user"

    def create_default_admin_users(self):
        try:
            try:
                if not MyUser.objects.filter(
                    username=EcommerceConstants.admin_user_details["username"]
                ).exists():
                    EcommerceConstants.admin_user_details.update(
                        {"user_id": uuid.uuid4()}
                    )
                    User.objects.create_superuser(
                        **EcommerceConstants.admin_user_details
                    )
                    user_query1 = MyUser.objects.get(
                        username=EcommerceConstants.admin_user_details["username"]
                    )
                    admin_serializer_data = UserSerializer(
                        user_query1,
                        remove_fields=["password", "groups", "user_permissions"],
                    ).data
                    admin_serializer_data.update(
                        {
                            key: int(admin_serializer_data[key])
                            for key in ["is_superuser", "is_staff", "is_active"]
                        }
                    )
                    redis_user_key = AccountsUtils.user_key_redis(admin_serializer_data)
                    admin_serializer_data = {
                        k: v for k, v in admin_serializer_data.items() if v != None
                    }
                    REDIS_CONNECTION_WRITE.hmset(redis_user_key, admin_serializer_data)
                    logging.info(
                        "System admin {} created successfully !!!".format(
                            EcommerceConstants.admin_user_details["username"]
                        )
                    )
            except Exception as error:
                logging.exception(
                    f"Exception occured while creating system admin {EcommerceConstants.admin_user_details['username']} {EcommerceConstants.LOG_LINES} {error}"
                )

            try:
                if not MyUser.objects.filter(
                    username=EcommerceConstants.debug_user_details["username"]
                ).exists():
                    User.objects.create_superuser(
                        **EcommerceConstants.debug_user_details
                    )
                    EcommerceConstants.debug_user_details.update(
                        {"user_id": uuid.uuid4()}
                    )
                    user_query2 = MyUser.objects.get(
                        username=EcommerceConstants.debug_user_details["username"]
                    )
                    debug_serializer_data = UserSerializer(
                        user_query2,
                        remove_fields=["password", "groups", "user_permissions"],
                    ).data
                    debug_serializer_data.update(
                        {
                            key: int(debug_serializer_data[key])
                            for key in ["is_superuser", "is_staff", "is_active"]
                        }
                    )
                    redis_user_key = AccountsUtils.user_key_redis(debug_serializer_data)
                    debug_serializer_data = {
                        k: v for k, v in debug_serializer_data.items() if v != None
                    }
                    REDIS_CONNECTION_WRITE.hmset(redis_user_key, debug_serializer_data)
                    logging.info(
                        "System admin {} created successfully !!!".format(
                            EcommerceConstants.debug_user_details["username"]
                        )
                    )
            except Exception as error:
                logging.exception(
                    f"Exception occured while creating system admin {EcommerceConstants.debug_user_details['username']} {EcommerceConstants.LOG_LINES} {error}"
                )
        except Exception as error:
            logging.exception(
                f"Exception occured while creating admin users {EcommerceConstants.LOG_LINES} {error}"
            )

    def create_system_config(self):
        try:
            if not SystemConfig.objects.filter(
                system_name=EcommerceConstants.system_config_details["system_name"]
            ).exists():
                serializer = SystemconfigSerializer(
                    data=EcommerceConstants.system_config_details
                )
                if serializer.is_valid():
                    serializer.save()
                    logging.info(EcommerceConstants.SYSTEM_CONFIG_SUCCESS)
        except Exception as error:
            logging.exception(
                f"Exception occured while creating system config {EcommerceConstants.LOG_LINES} {error}"
            )

    def handle(self, *args, **options):
        try:
            call_command("makemigrations")
            call_command("migrate")
            self.create_default_admin_users()
            self.create_system_config()
        except Exception as error:
            logging.error(error)

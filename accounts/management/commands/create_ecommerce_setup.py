import logging
import uuid

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from accounts import utils as AccountsUtils
from accounts.models import MyUser
from accounts.serializers import UserSerializer
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from system.models import SystemConfig
from system.serializers import SystemconfigSerializer

User = get_user_model()


class Command(BaseCommand):
    help = "This management command is used for creating Super user\
    and debug user"

    def create_default_admin_users(self):
        """
        Function to create default admin and debug users.
        """
        try:
            try:
                admin_user_details = EcommerceConstants.admin_user_details
                # Creating system admin user if it doesn't exist
                if not MyUser.objects.filter(
                    username=admin_user_details["username"]
                ).exists():
                    User.objects.create_superuser(**admin_user_details)
                    user_query1 = MyUser.objects.get(
                        username=admin_user_details["username"]
                    )
                    admin_serializer_data = UserSerializer(user_query1).data
                    AccountsUtils.set_user_info_to_redis(admin_serializer_data)
                    logging.info(
                        "System admin {} created successfully !!!".format(
                            admin_user_details["username"]
                        )
                    )
            except Exception as error:
                logging.exception(
                    "Exception occured while creating system admin {} {} {}".format(
                        admin_user_details["username"],
                        EcommerceConstants.LOG_LINES,
                        error,
                    )
                )

            try:
                debug_user_details = EcommerceConstants.debug_user_details
                # Creating debug user if it doesn't exist
                if not MyUser.objects.filter(
                    username=debug_user_details["username"]
                ).exists():
                    User.objects.create_superuser(**debug_user_details)
                    debug_user_details.update({"user_id": uuid.uuid4()})
                    user_query2 = MyUser.objects.get(
                        username=debug_user_details["username"]
                    )
                    debug_serializer_data = UserSerializer(user_query2).data
                    debug_serializer_data.update(
                        {
                            key: int(debug_serializer_data[key])
                            for key in ["is_superuser", "is_staff", "is_active"]
                        }
                    )
                    redis_user_key = AccountsUtils.user_key_redis(debug_serializer_data)
                    debug_serializer_data = {
                        k: v for k, v in debug_serializer_data.items() if v is not None
                    }
                    EcommerceSettings.REDIS_CONNECTION_WRITE.hmset(
                        redis_user_key, debug_serializer_data
                    )
                    logging.info(
                        "System admin {} created successfully !!!".format(
                            debug_user_details["username"]
                        )
                    )
            except Exception as error:
                logging.exception(
                    "Exception occured while creating system admin {} {} {}".format(
                        debug_user_details["username"],
                        EcommerceConstants.LOG_LINES,
                        error,
                    )
                )
        except Exception as error:
            logging.exception(
                "Exception occured while creating admin users {} {}".format(
                    EcommerceConstants.LOG_LINES, error
                )
            )

    def create_system_config(self):
        """
        Creates a system configuration.
        """
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
                f"Exception occured while creating system config\
                    {EcommerceConstants.LOG_LINES} {error}"
            )

    def handle(self, *args, **options):
        """
        Handles the execution of a series of Django management commands
        and custom tasks related to the system setup.
        """
        try:
            # Creating default admin users
            self.create_default_admin_users()

            # Creating the system configuration
            self.create_system_config()
        except Exception as error:
            logging.error(error)

import logging, pytz, json, uuid
from django.http import HttpRequest
from django.core.management import BaseCommand
from datetime import datetime
from e_commerce.constants import(
    admin_user_details, debug_user_details,
    LOG_LINES, system_config_details
)
from accounts.models import Myuser
from accounts.utils import (
    get_current_timestamp_of_timezone,
    hash_given_password, user_key_redis
)
from e_commerce.settings import (
    TIME_ZONE, REDIS_CONNECTION_WRITE
)
from accounts.serializers import UserSerializer
from django.core.management import call_command
from system.models import SystemConfig
from system.serializers import SystemconfigSerializer

class Command(BaseCommand):
    help = "This management command is used for creating Super user and debug user"

    def create_default_admin_users(self):
        try:
            user_request = HttpRequest()
            user_request.method = 'POST'
            try:
                if not Myuser.objects.filter(username = admin_user_details['username']).exists():
                    admin_user_details.update(
                        {
                            'user_id': uuid.uuid4(),
                            'password': hash_given_password(admin_user_details['password'])
                        }
                    )
                    serializer = UserSerializer(data = admin_user_details, context = {'request' : user_request})
                    if serializer.is_valid():
                        serializer.save()
                        serializer_data = serializer.data
                        serializer_data['is_superuser'] = int(serializer_data['is_superuser'])
                        redis_user_key = user_key_redis(serializer_data)
                        serializer_data = {k:v for k, v in serializer_data.items() if v != None}
                        REDIS_CONNECTION_WRITE.hmset(redis_user_key, serializer_data)
                        logging.info("System admin {} created successfully !!!".format(admin_user_details['username']))
                    else:
                        logging.exception(serializer.errors)
            except Exception as error:
                logging.exception(f"Exception occured while creating system admin {admin_user_details['username']} {LOG_LINES} {error}")
            
            try:
                if not Myuser.objects.filter(username = debug_user_details['username']).exists():
                    debug_user_details.update(
                        {
                            'user_id': uuid.uuid4(),
                            'password': hash_given_password(debug_user_details['password'])
                        }
                    )
                    debug_user_serializer = UserSerializer(data = debug_user_details, context = {'request' : user_request})
                    if debug_user_serializer.is_valid():
                        debug_user_serializer.save()
                        debug_user_serializer_data = debug_user_serializer.data
                        debug_user_serializer_data['is_superuser'] = int(debug_user_serializer_data['is_superuser'])
                        redis_user_key = user_key_redis(debug_user_serializer_data)
                        debug_user_serializer_data = {k:v for k, v in debug_user_serializer_data.items() if v != None}
                        REDIS_CONNECTION_WRITE.hmset(redis_user_key, debug_user_serializer_data)
                        logging.info("System admin {} created successfully !!!".format(debug_user_details['username']))
                    else:
                        logging.exception(serializer.errors)
            except Exception as error:
                logging.exception(f"Exception occured while creating system admin {debug_user_details['username']} {LOG_LINES} {error}")
        except Exception as error:
            logging.exception(f"Exception occured while creating admin users {LOG_LINES} {error}")

    def create_system_config(self):
        try:
            if not SystemConfig.objects.filter(system_name = system_config_details['system_name']).exists():
                serializer = SystemconfigSerializer(data=system_config_details)
                if serializer.is_valid():
                    serializer.save()
                    logging.info(f"System config created successfully !!!")
        except Exception as error:
            logging.exception(f"Exception occured while creating system config {LOG_LINES} {error}")

    def handle(self, *args, **options):
        try:
            call_command("makemigrations")
            call_command("migrate")
            self.create_default_admin_users()
            self.create_system_config()
        except Exception as error:
            logging.error(error)


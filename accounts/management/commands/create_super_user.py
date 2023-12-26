import logging, pytz, json, uuid
from django.http import HttpRequest
from django.core.management import BaseCommand
from datetime import datetime
from e_commerce.constants import admin_user_details, debug_user_details
from accounts.models import Myuser
from accounts.utils import (
    get_current_timestamp_of_timezone,
    hash_given_password, user_key_redis
)
from e_commerce.settings import (
    TIME_ZONE, REDIS_CONNECTION_WRITE
)
from accounts.serializers import UserSerializer


class Command(BaseCommand):
    help = "This management command is used for creating Super user and debug user"

    def handle(self, *args, **options):
        try:
            user_request = HttpRequest()
            user_request.method = 'POST'
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            created_time = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            try:
                if not Myuser.objects.filter(username = admin_user_details['username']).exists():
                    admin_user_details.update({'user_id': uuid.uuid4(), 'created_at': created_time,
                                          'password': hash_given_password(admin_user_details['password'])
                                          })
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
                    logging.info("System admin {} already exists !!!".format(admin_user_details['username']))
            except Exception as error:
                logging.exception("Exception occured while creating system admin {} Errors: {}".format(error))
            
            try:
                if not Myuser.objects.filter(username = debug_user_details['username']).exists():
                    debug_user_details.update({'user_id': uuid.uuid4(), 'created_at': created_time,
                                          'password': hash_given_password(admin_user_details['password'])
                                          })
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
                    logging.info("System admin {} already exists !!!".format(debug_user_details['username']))
            except Exception as error:
                logging.exception("Exception occured while creating system admin {} Errors: {}".format(error))

        except Exception as error:
            logging.error(error)


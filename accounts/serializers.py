
import logging
from django.db.models import Q
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import Myuser
from e_commerce.constants import (
    LOG_LINES,
    USER_ALREADY_EXISTS,
    USERNAME_ALREADY_EXISTS,
)

class UserSerializer(ModelSerializer):

    class Meta:
        model = Myuser
        fields = '__all__'

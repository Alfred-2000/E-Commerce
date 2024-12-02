import logging
from django.db.models import Q
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import MyUser
from e_commerce.constants import (
    LOG_LINES,
    USER_ALREADY_EXISTS,
    USERNAME_ALREADY_EXISTS,
)


class UserSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop("remove_fields", None)
        super(UserSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = MyUser
        fields = "__all__"

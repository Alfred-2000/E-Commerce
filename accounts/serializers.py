from rest_framework import serializers

from accounts import constants as AccountsConstants
from accounts.models import MyUser


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop("remove_fields", None)
        super(UserSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = MyUser
        fields = AccountsConstants.USERS_META_FIELDS

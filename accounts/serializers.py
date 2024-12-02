from django.db.models import Q
from rest_framework.serializers import ModelSerializer
from accounts.models import MyUser
from accounts import Constants as AccountsConstants


class UserSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop("remove_fields", None)
        super(UserSerializer, self).__init__(*args, **kwargs)
        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = MyUser
        fields = AccountsConstants.USERS_META_FIELDS

from rest_framework import serializers

from accounts import constants as AccountsConstants
from accounts.models import Address, MyUser
from utils.classes import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MyUser
        fields = AccountsConstants.USERS_META_FIELDS


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

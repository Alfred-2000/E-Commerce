from rest_framework import serializers

from system.models import SystemConfig


class SystemconfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = "__all__"

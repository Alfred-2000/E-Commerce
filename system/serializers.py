from system.models import SystemConfig
from rest_framework.serializers import ModelSerializer

class SystemconfigSerializer(ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'
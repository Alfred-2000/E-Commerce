
import logging
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import User
from e_commerce.constants import (
    DELIMITER,
    EMAIL_ALREADY_EXISTS,
    USERNAME_ALREADY_EXISTS,
)

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        if self._context["request"].method == 'POST':
            if User.objects.filter(username = attrs['username']).exists():
                logging.error(attrs['username'] + DELIMITER + USERNAME_ALREADY_EXISTS)
                raise ValidationError(USERNAME_ALREADY_EXISTS)
            
            if User.objects.filter(email = attrs['email']).exists():
                logging.error(attrs['email'] + DELIMITER + EMAIL_ALREADY_EXISTS)
                raise ValidationError(EMAIL_ALREADY_EXISTS)
            
        return attrs
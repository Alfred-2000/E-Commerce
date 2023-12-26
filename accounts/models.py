from django.db import models
from datetime import datetime
from django.db.models import DateTimeField

class DateTimeWithoutTZField(DateTimeField):
    def db_type(self, connection):
        return 'timestamptz'
    
class Myuser(models.Model):
    user_id = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=256, null=True, blank=True, unique=True)
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.TextField(blank=True, null=True, unique=True)
    is_superuser = models.BooleanField(default=False)
    created_at = DateTimeWithoutTZField(null=True, blank=True)
    updated_at = DateTimeWithoutTZField(null=True, blank=True)

    def __str__(self):
        return self.username
    


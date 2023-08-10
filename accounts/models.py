from django.db import models
from datetime import datetime
from django.db.models import DateTimeField

# class DateTimeWithoutTZField(DateTimeField):
#     def db_type(self, connection):
#         return 'timestamptz'
    
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=256, null=True, blank=True)
    date_joined = DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
    


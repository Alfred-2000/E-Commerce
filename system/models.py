import uuid
from datetime import datetime

from django.db import models

from system.utils import DateTimeWithTZField


class SystemConfig(models.Model):
    system_id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    system_name = models.CharField(max_length=150)
    smtp_enable = models.BooleanField(default=False)
    smtp_host = models.CharField(max_length=50)
    smtp_username = models.CharField(max_length=100)
    smtp_password = models.CharField(max_length=100)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)

    def __str__(self):
        return self.system_id

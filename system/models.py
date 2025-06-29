import uuid

from django.db import models

from utils import models as UtilitiesModels


class SystemConfig(UtilitiesModels.CommonAttributes):
    system_id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    system_name = models.CharField(max_length=150)
    smtp_enable = models.BooleanField(default=False)
    smtp_host = models.CharField(max_length=50)
    smtp_username = models.CharField(max_length=100)
    smtp_password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.system_id} - {self.system_name}"

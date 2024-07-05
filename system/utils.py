from django.db import models

class DateTimeWithTZField(models.DateTimeField):
    def db_type(self, connection):
        return 'timestamptz'
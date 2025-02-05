from django.db import models

FILTER_FIELD_TYPE_LOOKUP_MAP = {
    "number": ["in", "notin", "gt", "gte", "lt", "lte", "range", "notrange"],
    "string": ["in", "notin", "contains", "icontains", "startswith", "endswith"],
    "boolean": ["exact"],
    "timestamp": ["range"],
}

API_TYPES_MAPPING = {
    "int": "number",
    "float": "number",
    "string": "string",
    "bool": "boolean",
    "timestamp": "date-range",
    "bytes": "bytes",
    "date": "date-range",
    "time": "date-range",
    "timedelta": "duration",
    "file": "bytes",
    "uuid": "string",
}

DJANGO_FIELD_TO_PYTHON_TYPE = {
    models.AutoField: "int",
    models.BigAutoField: "int",
    models.BigIntegerField: "int",
    models.BinaryField: "bytes",
    models.BooleanField: "bool",
    models.CharField: "string",
    models.DateField: "date",
    models.DateTimeField: "timestamp",
    models.DecimalField: "float",
    models.DurationField: "timedelta",
    models.EmailField: "string",
    models.FileField: "file",
    models.FilePathField: "string",
    models.FloatField: "float",
    models.ImageField: "bytes",
    models.IntegerField: "int",
    models.GenericIPAddressField: "string",
    models.PositiveIntegerField: "int",
    models.PositiveSmallIntegerField: "int",
    models.SlugField: "string",
    models.SmallIntegerField: "int",
    models.TextField: "string",
    models.TimeField: "time",
    models.URLField: "string",
    models.UUIDField: "uuid",
}

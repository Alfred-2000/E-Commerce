from django.db import models

from utilities import classes as UtilitiesClasses
from utilities.classes import LookupExpression

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

FILTER_FIELD_TYPE_LOOKUP_MAP = {
    "number": [
        LookupExpression.IN,
        LookupExpression.NOTIN,
        LookupExpression.GT,
        LookupExpression.GTE,
        LookupExpression.LTE,
        LookupExpression.LT,
        LookupExpression.RANGE,
        LookupExpression.NOTRANGE,
    ],
    "string": [
        LookupExpression.IN,
        LookupExpression.NOTIN,
        LookupExpression.CONTAINS,
        LookupExpression.ICONTAINS,
        LookupExpression.NOTCONTAINS,
        LookupExpression.NOTICONTAINS,
        LookupExpression.CONTAINSIN,
        LookupExpression.ICONTAINSIN,
        LookupExpression.NOTCONTAINSIN,
        LookupExpression.NOTICONTAINSIN,
    ],
    "boolean": [
        LookupExpression.EXACT,
    ],
    "timestamp": [
        LookupExpression.RANGE,
    ],
}

DJANGO_FIELD_TO_PYTHON_TYPE: dict[type, str] = {
    models.AutoField: UtilitiesClasses.DataTypes.INT,
    models.BigAutoField: UtilitiesClasses.DataTypes.INT,
    models.BigIntegerField: UtilitiesClasses.DataTypes.INT,
    models.BinaryField: UtilitiesClasses.DataTypes.BYTES,
    models.BooleanField: UtilitiesClasses.DataTypes.BOOL,
    models.CharField: UtilitiesClasses.DataTypes.STRING,
    models.DateField: UtilitiesClasses.DataTypes.DATE,
    models.DateTimeField: UtilitiesClasses.DataTypes.TIMESTAMP,
    models.DecimalField: UtilitiesClasses.DataTypes.FLOAT,
    models.DurationField: UtilitiesClasses.DataTypes.TIMEDELTA,
    models.EmailField: UtilitiesClasses.DataTypes.STRING,
    models.FileField: UtilitiesClasses.DataTypes.FILE,
    models.FilePathField: UtilitiesClasses.DataTypes.STRING,
    models.FloatField: UtilitiesClasses.DataTypes.FLOAT,
    models.ImageField: UtilitiesClasses.DataTypes.BYTES,
    models.IntegerField: UtilitiesClasses.DataTypes.INT,
    models.GenericIPAddressField: UtilitiesClasses.DataTypes.STRING,
    models.PositiveIntegerField: UtilitiesClasses.DataTypes.INT,
    models.PositiveSmallIntegerField: UtilitiesClasses.DataTypes.INT,
    models.SlugField: UtilitiesClasses.DataTypes.STRING,
    models.SmallIntegerField: UtilitiesClasses.DataTypes.INT,
    models.TextField: UtilitiesClasses.DataTypes.STRING,
    models.TimeField: UtilitiesClasses.DataTypes.TIME,
    models.URLField: UtilitiesClasses.DataTypes.STRING,
    models.UUIDField: UtilitiesClasses.DataTypes.UUID,
}

import logging
from collections import OrderedDict

from django_filters import filters, filterset, Filter
from e_commerce import constants as EcommerceConstants

from django.db.models import QuerySet
from typing import Any
from utilities import constants as UtilitiesConstants
from utilities import utils as Utilities


class NotInFilter(Filter):
    def filter(self, qs: QuerySet, values: Any):
        if values:
            values = values.split(",")
            return qs.exclude(**{f"{self.field_name}__in": values})
        return qs


class GenericModelFilterSet(filterset.FilterSet):
    @classmethod
    def get_fields(cls):
        fields = cls._meta.fields
        if isinstance(fields, dict):
            fields = {name: lookups for name, lookups in fields.items()}
        elif isinstance(fields, list):
            field_types = Utilities.get_model_field_type(cls._meta.model, fields)
            fields = {
                field: UtilitiesConstants.FILTER_FIELD_TYPE_LOOKUP_MAP.get(type)
                for field, type in field_types.items()
            }
        return OrderedDict(fields)

    @classmethod
    def filter_for_field(cls, field, field_type, lookup_expr):
        """
        Override this method to provide custom filters based on field and lookup type.
        """
        if lookup_expr == "notin":
            return NotInFilter
        filter_class = super().filter_for_field(field, field_type, lookup_expr)
        return filter_class

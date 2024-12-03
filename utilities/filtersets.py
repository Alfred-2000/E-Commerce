import logging
from collections import OrderedDict

from django.db import models
from django_filters import BaseInFilter, BaseRangeFilter, FilterSet
from e_commerce import constants as EcommerceConstants

from utilities import constants as UtilitiesConstants


def field_to_python_type(field_type: type[models.Field]) -> str | None:
    """
    Function converts a Django model field type to its corresponding Python type.

    Input:
        field_type: type of a django model field

    Output:
        a string representing the python type if the field type
        is registered under the `DJANGO_FIELD_TO_PYTHON_TYPE` dictionary.
        None if the field is unregistered
    """
    data_type = None
    try:
        data_type = UtilitiesConstants.DJANGO_FIELD_TO_PYTHON_TYPE.get(field_type, None)
    except Exception as err:
        logging.info(f"Exception occured while get field to python type: {err}")
    return data_type


def model_to_python_types(model: type[models.Model]) -> dict:
    """
    Function converts the fields of a Django model to their corresponding Python types.

    Input:
        model : a type instance representing a django model class

    Output:
        field_types : A dictionary where keys are field names (str)
                and values are the Python data types
    """
    field_types = {}
    try:
        field_types = {
            field.name: field_to_python_type(type(field))
            for field in model._meta.fields
        }
    except Exception as error:
        logging.info(
            f"Exception occured while converting fields from django model type to python type: {error}"
        )
    return field_types


def model_to_api_types(model: type[models.Model]) -> dict:
    """
    Function converts all fields of a django model to their corresponding API types.

    Input:
        model : a django model whose fields need to be converted.

    Output:
        field_type : A dictionary mapping field names to their corresponding API type strings.
                Fields without a corresponding API type are mapped to None.
    """
    field_type = {}
    try:
        field_type = {
            field: UtilitiesConstants.API_TYPES_MAPPING.get(data_type)
            for field, data_type in model_to_python_types(model).items()
            if data_type
        }
    except Exception as er:
        logging.info(
            f"Exception occured while converting model fields to api type: {er}"
        )
    return field_type


class GenericModelFilterSet(FilterSet):
    @classmethod
    def get_fields(cls):
        """
        `get_fields` is responsible for determining the fields the filterset should
        contain and their supported lookup expressions. This is by default done using
        `Meta.fields`, `Meta.exclude` and `Meta.field_overrides` property on the Filterset.
        We override this to allow for all the fields from the `Meta.model` to be included
        by default and allow almost all the lookup_expr supported for each field based on
        their data_type. This is done using the `FILTER_FIELD_TYPE_LOOKUP_MAP` dictionary
        under `vu_commons/rest/constants.py`
        """
        fields, exclude = cls._meta.fields, cls._meta.exclude  # type: ignore
        if not (fields or exclude):
            return super().get_fields()

        if exclude and not fields:
            fields = EcommerceConstants.ALL_FIELDS

        exclude = exclude or []
        field_types = model_to_api_types(cls._meta.model)  # type: ignore
        if fields == EcommerceConstants.ALL_FIELDS:
            allowed_fields = set(field_types) - set(exclude)
        else:
            allowed_fields = set(fields) - set(exclude)

        if not isinstance(fields, dict):
            fields = {
                field: UtilitiesConstants.FILTER_FIELD_TYPE_LOOKUP_MAP[data_type]
                for field, data_type in field_types.items()
                if data_type in UtilitiesConstants.FILTER_FIELD_TYPE_LOOKUP_MAP
                and field in allowed_fields
            }
        else:
            fields = {
                name: lookups
                for name, lookups in fields.items()
                if name in allowed_fields
            }
        return OrderedDict(fields)

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        """
        With the introduction of custom lookups like `notrange` and `notin`
        we will have to tell the filterset which filter class to use for
        such lookup_expr. Hence we override the `filter_for_lookup` to provide
        the filterset with this info
        """
        filter_class, params = super().filter_for_lookup(field, lookup_type)
        if lookup_type == "notrange":
            return BaseRangeFilter, params
        elif lookup_type == "notin":
            return BaseInFilter, params
        return filter_class, params

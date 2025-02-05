from utilities import constants as UtilitiesConstants
from django.db import models
from functools import wraps


def get_field_type(field_type: str) -> str:
    """
    Function to retrieve the corresponding API field type based on the Django field type.

    Args:
        field_type (str): The Django field type (e.g., 'CharField', 'IntegerField').

    Returns:
        Optional[str]: The corresponding API field type if found, otherwise `None`.
    """
    django_fields = UtilitiesConstants.DJANGO_FIELD_TO_PYTHON_TYPE.get(field_type, None)
    field_type = UtilitiesConstants.API_TYPES_MAPPING.get(django_fields, None)
    return field_type


def get_model_field_type(model: type[models.Model], filter_fields: list) -> dict:
    """
    Retrieves a dictionary of field names and their corresponding API field types
    for the given Django model, filtered by a list of field names.

    This function iterates over all fields in the specified model, checks if each
    field's name is present in the `filter_fields` list, and if so, retrieves the
    corresponding API field type using the `get_field_type` function.

    Args:
        model (type[models.Model]): The Django model class whose fields
            are to be inspected.
        filter_fields (List[str]): A list of field names to filter which fields
            should be included.

    Returns:
        Dict[str, Optional[str]]: A dictionary where the keys are field names
            and the values are the corresponding API field types.
            If a type can't be determined, the value will be `None`.
    """
    fields_dict = {}
    for field in model._meta.fields:
        if field.name in filter_fields:
            fields_dict.update({field.name: get_field_type(type(field))})
    return fields_dict

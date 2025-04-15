import logging
from typing import Tuple, Optional

from django.db import models

from e_commerce import constants as EcommerceConstants


def get_record(
    model_class: models.Model, filters: dict
) -> Tuple[bool, Optional[models.Model]]:
    try:
        instance = model_class.objects.filter(**filters).first()
        return (True, instance)
    except Exception as error:
        logging.exception(
            f"Exception occured while getting record from table: {model_class.__name__} {EcommerceConstants.LOG_LINES} {error}"
        )
        return (False, None)


def create_record(
    model_class: models.Model, input_args
) -> Tuple[bool, Optional[models.Model]]:
    try:
        instance = model_class.objects.create(**input_args)
        return (True, instance)
    except Exception as error:
        logging.exception(
            f"Exception occured while creating record in table : {model_class.__name__} {EcommerceConstants.LOG_LINES} {error}"
        )
        return (False, None)


def update_record(
    model_class: models.Model, filters: dict, update_args: dict
) -> Tuple[bool, Optional[models.Model]]:
    try:
        instance = model_class.objects.filter(**filters).update(**update_args)
        return (True, instance)
    except Exception as error:
        logging.exception(
            f"Exception occured while updating record in table : {model_class.__name__} {EcommerceConstants.LOG_LINES} {error}"
        )
        return (False, None)

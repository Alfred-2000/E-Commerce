from e_commerce import constants as EcommerceConstants

USERS_META_FIELDS = [
    "user_id",
    "is_superuser",
    "username",
    "first_name",
    "last_name",
    "email",
    "is_staff",
    "is_active",
    "phone_code",
    "phone_number",
    "state",
    "country",
]

USER_FIELD_VALIDATION = {
    "username": EcommerceConstants.USERNAME_ALREADY_EXISTS,
    "email": EcommerceConstants.EMAIL_ALREADY_EXISTS,
    "phone_number": EcommerceConstants.PHONE_NUMBER_ALREADY_EXISTS,
}

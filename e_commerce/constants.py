
LOG_LINES = "::_____________"

ENCODE = 'encode'

DECODE = 'decode'

JWT_SECRECT_KEY = "A@!b$#cd&10"

USER_LOGGED_IN_SUCCESSFULLY = "User logged in successfully"

INVALID_CREDENTIALS = "Invalid credentials"

UNAUTHORISED_ACCESS = "Unauthorised access"

INVALID_TOKEN = "INVALID_TOKEN"

USER_REGISTERED_SUCCESSFULLY = "User registered successfully"

USER_DELETED_SUCCESSFULLY = "User deleted successfully"

USER_DOSENT_EXISTS = "User does not exists"

USERNAME_ALREADY_EXISTS = "User name already exists"

EMAIL_ALREADY_EXISTS = "E-mail already exists"

ACCOUNT_RETRIEVED_SUCCESSFULLY = "Account retrieved successfully"

PHONE_NUMBER_ALREADY_EXISTS = "Phone number already exists"

USER_ALREADY_EXISTS = "User already exists"

USER_UPDATED_SUCCESSFULLY = "User updated successfully"

PRODUCT_DETAILS_LISTED_SUCCESSFULLY = "Product details listed successfully"

PRODUCT_ADDED_SUCCESSFULLY = "Product added successfully"

PRODUCT_ALREADY_EXISTS = "Product already exists"

PRODUCT_UPDATED_SUCCESSFULLY = "Product updated successfully"

PRODUCT_DELETED_SUCCESSFULLY = "Product deleted successfully"

PRODUCTS_LISTED_SUCCESSFULLY = "Products listed successfully"

PRODUCT_DOESNT_EXISTS = "Product does not exists"

ORDER_DETAILS_LISTED_SUCCESSFULLY = "Order details listed successfully"

ORDER_ADDED_SUCCESSFULLY = "Order added successfully"

ORDER_UPDATED_SUCCESSFULLY = "Order updated successfully"

ORDER_DELETED_SUCCESSFULLY = "Order deleted successfully"

ORDERS_LISTED_SUCCESSFULLY = "Order listed successfully"

ORDER_DOESNT_EXISTS = "Order does not exists"

SYSTEM_CONFIG_SUCCESS = "System config created successfully !!!"

ORDER_STATUS = {
    0: "Order Placed",
    1: "Packing for dispatch",
    2: "Order Shipped",
    3: "Order reached to final destination",
    4: "Out for delivery",
    5: "Order Deliverd",
    6: "Order Cancelled"
}

admin_user_details = {
    "username": 'Super-Admin',
    "password": 'Ecommerce@!123',
    "email": 'eadmin@gmail.com',
    "phone_code": '+91',
    "phone_number": '9000000000',
    "is_superuser": True
}

debug_user_details = {
    "username": 'Debug-Admin',
    "password": 'Ecommerce@!123',
    "email": 'edebugadmin@gmail.com',
    "phone_code": '+91',
    "phone_number": '8000000000',
    "is_superuser": True
}

SMTP_HOST = 'gmail'
SMTP_USER = 'test123@gmail.com'
SMTP_PASSWORD = 'pkfagrthmgrinqse'

system_config_details = {
    'system_name': 'E-Commerce',
    'smtp_enable': True,
    'smtp_host': SMTP_HOST,
    'smtp_username': SMTP_USER,
    'smtp_password': SMTP_PASSWORD
}
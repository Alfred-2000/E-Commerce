from utils.classes import StrEnum

PRODUCT_SEARCH_AND_FILTER_FIELDS = [
    "name",
    "description",
]


class OrderStatus(StrEnum):
    CREATED = "Created"
    ORDER_PLACED = "Order Placed"
    AWAITING_PAYMENT = "Awaiting Payment"
    PAYMENT_FAILED = "Payment Failed"
    PACKING = "Packing for dispatch"
    SHIPPED = "Order Shipped"
    AT_DESTINATION = "Order reached to final destination"
    OUT_FOR_DELIVERY = "Out for delivery"
    DELIVERED = "Order Delivered"
    CANCELLED = "Order Cancelled"
    ON_HOLD = "On Hold"
    RETURNED = "Returned"
    REPLACED = "Replaced"

    @classmethod
    def choices(self):
        return [(status.value, status.value) for status in OrderStatus]

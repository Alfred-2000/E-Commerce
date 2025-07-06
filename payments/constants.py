from utils.classes import StrEnum


class TransactionStatus(StrEnum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    PENDING = "Pending"
    REFUNDED = "Refunded"
    CANCELLED = "Cancelled"
    PROCESSING = "Processing"
    DECLINED = "Declined"

    @classmethod
    def choices(self):
        return [(status.value, status.value) for status in TransactionStatus]

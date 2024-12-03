from enum import Enum, auto


class LowercaseStrEnum(Enum):
    def __str__(self):
        # Return the string representation of the enum in lowercase
        return self.name.lower()


class LookupExpression(LowercaseStrEnum):
    CONTAINS = auto()
    ICONTAINS = auto()
    NOTCONTAINS = auto()
    NOTICONTAINS = auto()
    CONTAINSIN = auto()
    ICONTAINSIN = auto()
    NOTCONTAINSIN = auto()
    NOTICONTAINSIN = auto()
    EXACT = auto()
    IN = auto()
    RANGE = auto()
    LT = auto()
    LTE = auto()
    GTE = auto()
    GT = auto()
    NOTIN = auto()
    NOTRANGE = auto()


class DataTypes(LowercaseStrEnum):
    """
    A simple enum representing all the
    commonly used python data types as
    lower case string
    """

    BYTES = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    DATE = auto()
    TIME = auto()
    TIMESTAMP = auto()
    TIMEDELTA = auto()
    FILE = auto()
    UUID = auto()

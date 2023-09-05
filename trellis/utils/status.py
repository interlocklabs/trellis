from enum import Enum

class Status(Enum):
    PENDING = 0
    EXECUTING = 1
    SUCCESS = 2
    FAILED = 3
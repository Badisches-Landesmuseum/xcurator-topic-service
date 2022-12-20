from enum import Enum


class DetectionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED",
    PENDING = "PENDING",
    DONE = "DONE",
    VERIFIED = "VERIFIED",
    ERROR = "ERROR"

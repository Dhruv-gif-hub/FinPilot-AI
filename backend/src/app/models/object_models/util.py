from enum import Enum


class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"

    
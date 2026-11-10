import enum

class DocumentStatus(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
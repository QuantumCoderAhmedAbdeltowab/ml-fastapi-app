# from enum import Enum
# from typing import List, Optional
# from pydantic import BaseModel, Field

# class Role(str, Enum):
#     user = "user"
#     assistant = "assistant"

# class Message(BaseModel):
#     role: Role
#     content: str

# class ChatRequest(BaseModel):
#     question: str
#     history: Optional[List[Message]] = Field(default_factory=list)

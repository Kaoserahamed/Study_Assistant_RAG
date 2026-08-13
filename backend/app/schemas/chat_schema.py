# app/schemas/chat_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Citation(BaseModel):
    """Citation matching frontend format"""
    id: str
    documentId: str
    documentTitle: str
    documentKind: str
    page: int
    snippet: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    citations: List[Citation] = Field(default_factory=list)


class ChatResponse(BaseModel):
    message_id: int
    user_message_id: int
    content: str
    citations: List[Citation]


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse]


class SendMessageRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None

# app/routers/chat_router.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.services.chat_service import ChatService
from app.schemas.chat_schema import (
    SendMessageRequest,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
    CreateConversationRequest,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new conversation"""
    service = ChatService(db)
    conversation = service.create_conversation(current_user["id"], request.title)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all conversations for current user"""
    service = ChatService(db)
    conversations = service.get_user_conversations(current_user["id"])
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get conversation with all messages"""
    service = ChatService(db)
    conversation = service.get_conversation(conversation_id, current_user["id"])
    messages = service.get_conversation_messages(conversation_id, current_user["id"])
    
    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=messages
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a conversation"""
    service = ChatService(db)
    service.delete_conversation(conversation_id, current_user["id"])


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Send a message and get AI response (async)"""
    service = ChatService(db)
    result = await service.send_message_async(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        query=request.query,
        document_ids=request.document_ids
    )
    return result

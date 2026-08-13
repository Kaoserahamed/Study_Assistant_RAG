# app/repositories/message_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.message import Message, RoleEnum


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        role: RoleEnum,
        content: str,
        citations: list = None
    ) -> Message:
        """Create a new message"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation(self, conversation_id: int) -> List[Message]:
        """Get all messages in a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()

    def get_recent(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """Get recent messages in a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

    def delete_by_conversation(self, conversation_id: int) -> None:
        """Delete all messages in a conversation"""
        self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete()
        self.db.commit()

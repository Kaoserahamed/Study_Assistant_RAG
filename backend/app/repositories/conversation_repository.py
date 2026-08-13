# app/repositories/conversation_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get conversation by ID (for authorized user only)"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_all_by_user(self, user_id: int) -> List[Conversation]:
        """Get all conversations for a user"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).all()

    def update(self, conversation: Conversation) -> Conversation:
        """Update conversation"""
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete(self, conversation: Conversation) -> None:
        """Delete conversation"""
        self.db.delete(conversation)
        self.db.commit()

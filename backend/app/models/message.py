# app/models/message.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class RoleEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

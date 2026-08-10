# app/models/database_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database_models import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    conversations = relationship("Conversation", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200), nullable=False)
    chunk_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    status = Column(String(20), default="success")
    create_time = Column(DateTime, default=datetime.now)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), default="新对话")
    create_time = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    conversation = relationship("Conversation", back_populates="messages")
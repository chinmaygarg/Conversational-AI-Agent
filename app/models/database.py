from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class Language(str, enum.Enum):
    HINDI = "hi"
    ENGLISH = "en"
    MIXED = "mixed"

class DocumentType(str, enum.Enum):
    FAQ = "faq"
    POLICY = "policy"
    MANUAL = "manual"
    CRM = "crm"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    language = Column(Enum(Language), default=Language.MIXED)
    metadata = Column(JSON)
    
    messages = relationship("Message", back_populates="conversation")
    api_logs = relationship("APILog", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    audio_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    
    conversation = relationship("Conversation", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    doc_type = Column(Enum(DocumentType))
    language = Column(Enum(Language))
    embedding = Column(JSON)  # Store vector embeddings
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    endpoint = Column(String)
    method = Column(String)
    request_data = Column(JSON)
    response_data = Column(JSON)
    status_code = Column(Integer)
    latency = Column(Integer)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="api_logs")

class FunctionCall(Base):
    __tablename__ = "function_calls"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    function_name = Column(String)
    parameters = Column(JSON)
    result = Column(JSON)
    status = Column(String)  # success, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation") 
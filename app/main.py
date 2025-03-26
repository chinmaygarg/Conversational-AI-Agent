from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import numpy as np
import soundfile as sf
import io
import uuid
import os

from app.core.config import settings
from app.core.database import get_db
from app.models.database import Language, Document
from app.services.speech_recognition import SpeechRecognitionService
from app.services.rag import RAGService
from app.services.tts import TextToSpeechService

app = FastAPI(
    title="Bilingual Speech Recognition & Response Generation System",
    description="API for real-time Hindi/English speech recognition, response generation, and text-to-speech",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize services
speech_recognition = SpeechRecognitionService()
tts_service = TextToSpeechService()

@app.get("/")
async def read_root():
    """Serve the main web interface."""
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/api/v1/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[Language] = None,
    db: Session = Depends(get_db)
):
    """
    Convert speech to text with language detection.
    
    Args:
        audio: Audio file (WAV format)
        language: Optional language hint
        db: Database session
        
    Returns:
        Transcribed text and detected language
    """
    try:
        # Read audio file
        audio_data, sample_rate = sf.read(io.BytesIO(await audio.read()))
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Transcribe
        text, detected_language = await speech_recognition.transcribe_audio(
            audio_data,
            sample_rate=sample_rate,
            language=language
        )
        
        return {
            "text": text,
            "language": detected_language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/text-to-speech")
async def text_to_speech(
    text: str,
    language: Optional[Language] = None,
    voice_id: Optional[str] = None,
    speed: float = 1.0,
    pitch: float = 1.0
):
    """
    Convert text to speech.
    
    Args:
        text: Text to convert to speech
        language: Language of the text
        voice_id: Optional voice ID to use
        speed: Speech speed multiplier
        pitch: Speech pitch multiplier
        
    Returns:
        Audio data
    """
    try:
        audio_data = await tts_service.generate_speech(
            text=text,
            language=language,
            voice_id=voice_id,
            speed=speed,
            pitch=pitch
        )
        
        return audio_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat")
async def chat(
    text: str,
    session_id: Optional[str] = None,
    language: Optional[Language] = None,
    db: Session = Depends(get_db)
):
    """
    Chat with the AI agent using RAG.
    
    Args:
        text: User's message
        session_id: Optional session ID for conversation history
        language: Optional language hint
        db: Database session
        
    Returns:
        AI response and audio
    """
    try:
        # Initialize RAG service
        rag_service = RAGService(db)
        
        # Get conversation history
        conversation_history = []
        if session_id:
            # TODO: Implement conversation history retrieval
            pass
        
        # Generate response
        response_text = await rag_service.generate_response(
            query=text,
            conversation_history=conversation_history,
            language=language
        )
        
        # Generate speech
        audio_data = await tts_service.generate_speech(
            text=response_text,
            language=language
        )
        
        return {
            "text": response_text,
            "audio": audio_data,
            "session_id": session_id or str(uuid.uuid4())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ingest-document")
async def ingest_document(
    title: str,
    content: str,
    doc_type: str,
    language: Language,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Ingest a document into the RAG system.
    
    Args:
        title: Document title
        content: Document content
        doc_type: Type of document (FAQ, policy, etc.)
        language: Language of the document
        metadata: Optional metadata
        db: Database session
        
    Returns:
        Ingested document
    """
    try:
        rag_service = RAGService(db)
        document = await rag_service.ingest_document(
            title=title,
            content=content,
            doc_type=doc_type,
            language=language,
            metadata=metadata
        )
        
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents")
async def list_documents(
    doc_type: Optional[str] = None,
    language: Optional[Language] = None,
    db: Session = Depends(get_db)
):
    """
    List documents in the RAG system.
    
    Args:
        doc_type: Filter by document type
        language: Filter by language
        db: Database session
        
    Returns:
        List of documents
    """
    try:
        query = db.query(Document)
        
        if doc_type:
            query = query.filter(Document.doc_type == doc_type)
        if language:
            query = query.filter(Document.language == language)
            
        documents = query.all()
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
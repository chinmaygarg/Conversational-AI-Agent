import torch
import whisper
import numpy as np
from typing import Tuple, Optional
import logging
from app.core.config import settings
from app.models.database import Language

logger = logging.getLogger(__name__)

class SpeechRecognitionService:
    def __init__(self):
        self.model = whisper.load_model(settings.ASR_MODEL)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
    async def transcribe_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[Language] = None
    ) -> Tuple[str, Language]:
        """
        Transcribe audio to text and detect language.
        
        Args:
            audio_data: numpy array of audio data
            sample_rate: sample rate of audio
            language: optional language hint
            
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        try:
            # Prepare audio for model
            if sample_rate != 16000:
                audio_data = self._resample_audio(audio_data, sample_rate)
            
            # Transcribe with language detection
            result = self.model.transcribe(
                audio_data,
                language=language.value if language else None,
                task="transcribe",
                fp16=self.device == "cuda"
            )
            
            # Detect language if not provided
            detected_language = self._detect_language(result["text"])
            
            return result["text"], detected_language
            
        except Exception as e:
            logger.error(f"Error in speech recognition: {str(e)}")
            raise
    
    def _resample_audio(self, audio_data: np.ndarray, target_rate: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(1, -1)
        
        # Simple linear interpolation for resampling
        if target_rate != 16000:
            ratio = 16000 / target_rate
            new_length = int(len(audio_data[0]) * ratio)
            indices = np.linspace(0, len(audio_data[0]) - 1, new_length)
            audio_data = np.interp(indices, np.arange(len(audio_data[0])), audio_data[0])
            audio_data = audio_data.reshape(1, -1)
        
        return audio_data
    
    def _detect_language(self, text: str) -> Language:
        """Detect language from text using simple heuristics."""
        # Count Hindi and English characters
        hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        english_chars = sum(1 for c in text if c.isascii())
        
        if hindi_chars > english_chars:
            return Language.HINDI
        elif english_chars > hindi_chars:
            return Language.ENGLISH
        else:
            return Language.MIXED
    
    async def process_streaming_audio(
        self,
        audio_chunks: list[np.ndarray],
        sample_rate: int = 16000
    ) -> Tuple[str, Language]:
        """
        Process streaming audio chunks for real-time transcription.
        
        Args:
            audio_chunks: list of audio chunks
            sample_rate: sample rate of audio chunks
            
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        # Concatenate chunks
        audio_data = np.concatenate(audio_chunks)
        return await self.transcribe_audio(audio_data, sample_rate) 
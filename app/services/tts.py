import os
import logging
from typing import Optional
import requests
from app.core.config import settings
from app.models.database import Language

logger = logging.getLogger(__name__)

class TextToSpeechService:
    def __init__(self):
        self.api_key = settings.RESEMBLE_AI_API_KEY
        self.base_url = "https://api.resemble.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    async def generate_speech(
        self,
        text: str,
        language: Optional[Language] = None,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bytes:
        """
        Generate speech from text using Resemble.AI API.
        
        Args:
            text: Text to convert to speech
            language: Language of the text
            voice_id: Optional voice ID to use
            speed: Speech speed multiplier
            pitch: Speech pitch multiplier
            
        Returns:
            Audio data as bytes
        """
        try:
            # Add SSML tags for better prosody
            ssml_text = self._add_ssml_tags(text, language)
            
            # Prepare request payload
            payload = {
                "text": ssml_text,
                "voice_id": voice_id or self._get_default_voice(language),
                "speed": speed,
                "pitch": pitch
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/speech",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"TTS API error: {response.text}")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
    
    def _add_ssml_tags(self, text: str, language: Optional[Language] = None) -> str:
        """Add SSML tags for better prosody."""
        # Add pauses between sentences
        text = text.replace(".", "<break time='500ms'/>.")
        text = text.replace("!", "<break time='500ms'/>!")
        text = text.replace("?", "<break time='500ms'/>?")
        
        # Add language-specific prosody
        if language == Language.HINDI:
            # Add Hindi-specific prosody
            text = f"<prosody rate='medium' pitch='medium'>{text}</prosody>"
        elif language == Language.ENGLISH:
            # Add English-specific prosody
            text = f"<prosody rate='medium' pitch='medium'>{text}</prosody>"
        else:
            # Default prosody for mixed language
            text = f"<prosody rate='medium' pitch='medium'>{text}</prosody>"
        
        return f"<speak>{text}</speak>"
    
    def _get_default_voice(self, language: Optional[Language] = None) -> str:
        """Get default voice ID based on language."""
        # TODO: Implement voice selection logic
        # This is a placeholder that should be replaced with actual voice selection
        if language == Language.HINDI:
            return "hindi-voice-id"
        elif language == Language.ENGLISH:
            return "english-voice-id"
        else:
            return "default-voice-id"
    
    async def clone_voice(
        self,
        audio_samples: list[bytes],
        name: str,
        language: Optional[Language] = None
    ) -> str:
        """
        Clone a voice from audio samples.
        
        Args:
            audio_samples: List of audio samples for voice cloning
            name: Name for the cloned voice
            language: Language of the voice samples
            
        Returns:
            Voice ID of the cloned voice
        """
        try:
            # Prepare request payload
            payload = {
                "name": name,
                "language": language.value if language else "mixed",
                "samples": [
                    {
                        "audio": self._encode_audio(audio)
                    }
                    for audio in audio_samples
                ]
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/voices",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Voice cloning API error: {response.text}")
            
            return response.json()["voice_id"]
            
        except Exception as e:
            logger.error(f"Error cloning voice: {str(e)}")
            raise
    
    def _encode_audio(self, audio_data: bytes) -> str:
        """Encode audio data to base64."""
        import base64
        return base64.b64encode(audio_data).decode('utf-8') 
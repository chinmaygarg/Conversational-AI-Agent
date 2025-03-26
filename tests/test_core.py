import pytest
import numpy as np
import soundfile as sf
import io
from app.services.speech_recognition import SpeechRecognitionService
from app.services.tts import TextToSpeechService
from app.models.database import Language

@pytest.fixture
def speech_recognition():
    return SpeechRecognitionService()

@pytest.fixture
def tts_service():
    return TextToSpeechService()

def test_language_detection():
    """Test language detection functionality."""
    sr = SpeechRecognitionService()
    
    # Test Hindi text
    hindi_text = "नमस्ते, मैं आपकी कैसे मदद कर सकता हूं?"
    assert sr._detect_language(hindi_text) == Language.HINDI
    
    # Test English text
    english_text = "Hello, how can I help you?"
    assert sr._detect_language(english_text) == Language.ENGLISH
    
    # Test mixed text
    mixed_text = "Hello, मैं आपकी कैसे मदद कर सकता हूं?"
    assert sr._detect_language(mixed_text) == Language.MIXED

@pytest.mark.asyncio
async def test_speech_recognition(speech_recognition):
    """Test speech recognition functionality."""
    # Create a simple sine wave as test audio
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)
    
    # Save as WAV file in memory
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
    wav_buffer.seek(0)
    
    # Test transcription
    text, language = await speech_recognition.transcribe_audio(
        audio_data,
        sample_rate=sample_rate
    )
    
    assert isinstance(text, str)
    assert isinstance(language, Language)

@pytest.mark.asyncio
async def test_text_to_speech(tts_service):
    """Test text-to-speech functionality."""
    # Test Hindi text
    hindi_text = "नमस्ते, मैं आपकी कैसे मदद कर सकता हूं?"
    audio_data = await tts_service.generate_speech(
        text=hindi_text,
        language=Language.HINDI
    )
    assert isinstance(audio_data, bytes)
    assert len(audio_data) > 0
    
    # Test English text
    english_text = "Hello, how can I help you?"
    audio_data = await tts_service.generate_speech(
        text=english_text,
        language=Language.ENGLISH
    )
    assert isinstance(audio_data, bytes)
    assert len(audio_data) > 0

def test_ssml_generation(tts_service):
    """Test SSML tag generation."""
    text = "Hello. How are you?"
    ssml = tts_service._add_ssml_tags(text)
    
    assert "<speak>" in ssml
    assert "<break time='500ms'/>" in ssml
    assert "<prosody" in ssml
    assert text in ssml

@pytest.mark.asyncio
async def test_voice_cloning(tts_service):
    """Test voice cloning functionality."""
    # Create test audio samples
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)
    
    # Save as WAV file in memory
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
    wav_buffer.seek(0)
    
    # Test voice cloning
    voice_id = await tts_service.clone_voice(
        audio_samples=[wav_buffer.getvalue()],
        name="test_voice",
        language=Language.ENGLISH
    )
    
    assert isinstance(voice_id, str)
    assert len(voice_id) > 0 
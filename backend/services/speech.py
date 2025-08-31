import os
from typing import Union, BinaryIO, Optional
import logging
from pathlib import Path
import tempfile

from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_USE_API = os.getenv("WHISPER_USE_API", "true").lower() == "true"

# Configure logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def transcribe_audio(file_path_or_bytes: Union[str, bytes, BinaryIO]) -> str:
    """
    Transcribe audio using Whisper API or return stub for testing
    
    Args:
        file_path_or_bytes: Path to audio file or bytes/file object
    
    Returns:
        Transcribed text
    """
    # Check if we should use the API
    if not WHISPER_USE_API:
        logger.warning("Whisper API disabled, using stub transcription")
        return _get_stub_transcription()
    
    # Check if API key is available
    if not OPENAI_API_KEY or not client:
        logger.warning("OpenAI API key missing, using stub transcription")
        return _get_stub_transcription()
    
    try:
        # Handle different input types
        if isinstance(file_path_or_bytes, (str, Path)):
            # It's a file path
            with open(file_path_or_bytes, "rb") as audio_file:
                return _call_whisper_api(audio_file)
        elif isinstance(file_path_or_bytes, bytes):
            # It's bytes, write to temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
                temp_file.write(file_path_or_bytes)
                temp_file.flush()
                with open(temp_file.name, "rb") as audio_file:
                    return _call_whisper_api(audio_file)
        else:
            # Assume it's a file-like object
            return _call_whisper_api(file_path_or_bytes)
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Error transcribing audio: {str(e)}"


def _call_whisper_api(audio_file: BinaryIO) -> str:
    """Call Whisper API with the audio file"""
    try:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
        return response.text
    except Exception as e:
        logger.error(f"Whisper API error: {e}")
        raise


def _get_stub_transcription() -> str:
    """Return a stub transcription for testing"""
    return """
    This is a stub transcription for testing purposes.
    
    In a real environment, this would contain the transcribed text from the audio file.
    
    Some key points:
    - We should implement feature X by next quarter
    - The team agreed to use technology Y for the project
    - John will follow up with the client about requirements
    - Next meeting scheduled for Friday at 2pm
    
    Action items:
    - Update the project roadmap
    - Share the design documents with the team
    - Schedule follow-up with stakeholders
    """

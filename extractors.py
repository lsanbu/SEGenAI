from io import BytesIO
from typing import Tuple
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from openai import OpenAI
import os

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(file_bytes: bytes, filename: str = "audio.webm") -> str:
    client = get_client()
    try:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=(filename, file_bytes)
        )
        return transcript.text.strip()
    except Exception:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, file_bytes)
        )
        return transcript.text.strip()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pypdf."""
    reader = PdfReader(BytesIO(file_bytes))
    chunks = []
    for page in reader.pages:
        try:
            text = page.extract_text()
            if text:
                chunks.append(text)
        except Exception:
            continue
    return "\n".join(chunks).strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    bio = BytesIO(file_bytes)
    doc = Document(bio)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()

def transcribe_audio(file_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Uses OpenAI's transcription.
    Models commonly available:
    - "whisper-1"
    - "gpt-4o-transcribe" (if your account has it)
    """
    try:
        transcript = _client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=(filename, file_bytes)
        )
        return transcript.text.strip()
    except Exception:
        transcript = _client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, file_bytes)
        )
        return transcript.text.strip()

def consolidate_inputs(typed_text: str, doc_text: str, audio_text: str) -> str:
    """Merge typed, doc, and audio text into one aggregated string."""
    blocks = []
    if typed_text and typed_text.strip():
        blocks.append(f"[TYPED]\n{typed_text.strip()}")
    if doc_text and doc_text.strip():
        blocks.append(f"[DOC]\n{doc_text.strip()}")
    if audio_text and audio_text.strip():
        blocks.append(f"[AUDIO]\n{audio_text.strip()}")
    return "\n\n".join(blocks).strip()

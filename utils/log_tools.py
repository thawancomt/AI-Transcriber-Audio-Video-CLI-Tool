from faster_whisper.transcribe import TranscriptionInfo, Segment
from typing import TypedDict
from math import ceil
import sys

import os


class TranscriptData(TypedDict):
    pct: str
    segment: Segment

def show_media_info(info: TranscriptionInfo):
    # Information about file, language and duration
    print(f"🌐 Detected language: {info.language}")
    print(f"📼 Duração da mídia: {info.duration / 60:.2f}m")


def show_presentation():
    """Show software presentation on terminal"""

    # Presentation
    os.system("cls" if os.name == "nt" else "clear")
    print("🎤 Transcritor de Áudio/Vídeo para Legendas")
    print("=" * 50)


def show_transcript_status(data: TranscriptData):
    """ show real time status"""
    from utils import TerminalTools as TT

    # Terminal tools
    TT.clear_terminal_line()
    bar_text = f"[{'|' * ceil(ceil(data['pct']) / 10)}{' ' * ceil((100 - ceil(data['pct'])) / 10)}]"
    msg = f"[ Progress: {ceil(data['pct'])}% ] - Transcription: {data['segment'].text[:40]}..."
    sys.stdout.write("\r" + bar_text + " " + msg)
    sys.stdout.flush()

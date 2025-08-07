
import os
from typing import TypedDict

from rich.console import Console

console = Console()

class Segment(TypedDict):
    """A single transcript segment."""
    text: str


class TranscriptionInfo():
    """Metadata about the audio/video file."""
    language: str
    duration: int   # seconds


class TranscriptData(TypedDict):
    """Real-time status sent to the terminal."""
    pct: int        # 0–100 inclusive
    segment: Segment



def show_media_info(info: TranscriptionInfo) -> None:
    """
    Print a short header describing the media file.

    Parameters
    ----------
    info : TranscriptionInfo
        The metadata dictionary.
    """
    console.print(f"🌐 [bold green] Detected language: [bold purple]{info.language}")
    console.print(f"📼 [bold yellow] Duração da mídia: {info.duration / 60:.2f}m")


def show_presentation():
    """Show software presentation on terminal"""

    # Presentation
    os.system("cls" if os.name == "nt" else "clear")
    console.print("🎤 [bold green] Transcritor de Áudio/Vídeo para Legendas")
    console.print("[bold yellow]=" * 50)

def build_progress_bar():
    pass
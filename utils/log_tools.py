
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
    console.print(f"📼 [bold yellow] Media length: {(info.duration // 60):.0f}:{info.duration % 60:.0f}m")


def show_presentation():
    """Show software presentation on terminal"""

    # Presentation
    clear_terminal()
    console.print("🎤 [bold green] AI Audio & Video Transcriptor")
    console.print("[bold yellow]=" * 50)


def show_transcription_operation_details(model : str):
    console.print(f"[bold yellow]Loading model: {model}")


def clear_terminal():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")
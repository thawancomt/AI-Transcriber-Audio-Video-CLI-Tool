import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from utils.log_tools import show_media_info


# Inicializa o console do Rich para uma saída bonita
console = Console()

try:
    from faster_whisper import WhisperModel
    from faster_whisper.transcribe import Segment
except ImportError:
    console.print(
        "[bold red]faster-whisper package not found, run ´uv´ to sync dependencies"
    )
    sys.exit(1)

MODELS_OPTIONS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")
ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]


@dataclass
class TranscriptOptions:
    """
    This class intend to help how to setup the config that whisper model need to prorpely work
    Before pass diferent configs, check user hardware.
    """

    device: Literal["cpu", "cuda"]
    compute_type: str
    model_size_or_path: ModelSize
    cpu_threads: int


@dataclass
class RunTranscriptOptions:
    """
    This class exists to help with lint and guide a more natural way to setup a personalized behavior of
    the transcription process.

    params:
        - file : The target file to be transcripted
        - whisper_models : the options to run the whisper model, see more details on (TranscriptOptions)
        - export_fmt : export format file type that  user desire
        - output_directory : the directory where user transcripted file will be saved
    """

    file: Path
    whisper_options: TranscriptOptions


def run_transcription(params: RunTranscriptOptions) -> Iterator[Segment]:
    """
    This function orchestrates the transcription process by loading the necessary model,
    processing the audio file, and saving the transcription output.

    params:
        - params : RunTranscriptOptions object containing all necessary parameters for transcription
    """

    # Loading model
    try:
        console.print(
            f"\n🤖 Carregando modelo '[bold cyan]{params.whisper_options.model_size_or_path}[/bold cyan]' ({params.whisper_options.device})… usando cpu : {params.whisper_options.cpu_threads}"
        )

        # Carregamento do modelo
        model = WhisperModel(
            params.whisper_options.model_size_or_path,
            device=params.whisper_options.device,
            compute_type=params.whisper_options.compute_type,
            cpu_threads=params.whisper_options.cpu_threads,
        )

    except Exception as e:
        console.print(
            f"❌ [bold red]Erro crítico ao carregar o modelo de IA:[/bold red] {e}"
        )
        sys.exit(1)

    # Processo de transcrição
    console.print("🚀 [bold green]Iniciando transcrição...[/bold green]")
    segments, media_info = model.transcribe(str(params.file), beam_size=5)

    show_media_info(
        info=media_info
    )  # Você pode refatorar esta função para usar o console.print também

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        
        transcription_task = progress.add_task(
            "[cyan]Transcrevendo...", total=media_info.duration
        )

        for segment in segments:
            yield segment

            progress.update(transcription_task, completed=segment.end)

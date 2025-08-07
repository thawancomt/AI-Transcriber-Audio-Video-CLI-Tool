import sys
from _io import TextIOWrapper
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from utils.log_tools import show_media_info

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
    export_fmt: str
    output_directory: Path


def _write_srt(file: TextIOWrapper, index, start_time, end_time, content):
    """"""
    text = f"""{index}\n{start_time} --> {end_time}\n{content}\n\n"""
    file.write(text)
    return file


def _write_txt(file: TextIOWrapper, content):
    """Write on txt files"""
    file.write(content)
    return file


def write_file(
    file: TextIOWrapper,
    content,
    file_format: str = "txt",
    start_time=None,
    end_time=None,
    index=None,
):
    if file_format == "srt":
        _write_srt(
            file=file,
            index=index,
            start_time=start_time,
            end_time=end_time,
            content=content,
        )
    else:
        _write_txt(file=file, content=content)
        return file


def save_from_tmp_file(tmp: Path, file: Path, export_format: str, output_dir):
    # Resigning the file name from temp filename to final version filename
    final_filename = Path(f"{file.stem}" + "." + export_format)

    destination_path = Path(output_dir) / final_filename

    try:
        tmp.replace(destination_path)
    except Exception as e:
        print(f"❌ Erro ao processar transcrição: {e}")


def run_transcription(params: RunTranscriptOptions):
    """
    Carrega as dependências pesadas e executa o processo de transcrição,
    usando uma barra de progresso do Rich.
    """
    # Inicializa o console do Rich para uma saída bonita
    console = Console()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        console.print(
            "[bold red]faster-whisper package not found, run ´uv´ to sync dependencies"
        )
        sys.exit(1)

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

    temp_file = Path(f"{params.file.stem}.tmp")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Adicionamos uma "tarefa" à barra de progresso.
        # O 'total' é a duração do vídeo em segundos, que nós conhecemos!
        transcription_task = progress.add_task(
            "[cyan]Transcrevendo...", total=media_info.duration
        )

        with open(temp_file, "w", encoding="utf-8") as f:
            for idx, segment in enumerate(segments):
                # Escreve o segmento no ficheiro
                write_file(
                    content=segment.text,
                    end_time=segment.end,
                    file=f,
                    file_format=params.export_fmt,
                    index=idx,
                    start_time=segment.start,
                )

                # Atualiza a barra de progresso, dizendo a ela em que ponto do tempo estamos.
                progress.update(transcription_task, completed=segment.end)

    # --- Finalização Segura ---
    destination_path = (
        Path(params.output_directory) / f"{params.file.stem}.{params.export_fmt}"
    )
    try:
        temp_file.replace(destination_path)
        console.print(
            f"\n✅ [bold green]Transcrição salva com sucesso em:[/bold green] '{destination_path}'"
        )
    except Exception as e:
        console.print(f"\n❌ [bold red]Erro ao salvar o ficheiro final:[/bold red] {e}")

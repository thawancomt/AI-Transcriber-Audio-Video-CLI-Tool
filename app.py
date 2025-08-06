"""
Este app tem como objetivo transcrever os videos/audios das aulas da faculdade.

Tech stack:
 - faster_whisper : Wrapper do Whisper para facilitar o uso


Requisitos:
- Transcrever audio e videos V
- Opção de seleção de qual video ou audio sera transcrito V
- Salvar a transcrição em arquivos srt V
- log visual para o usuario saber em qual etapa da transcrição o script está V

"""

import argparse
import sys
from pathlib import Path
from typing import List, Literal, TypedDict

import av.error
import psutil
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from utils.io_tools import (
    create_necessary_dirs,
    get_valid_files,
    organize_files,
    select_file_prompt,
)
from utils.log_tools import (
    show_media_info,
    show_presentation,
)
from utils.transcript_tools import write_file

MODELS_OPTIONS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")
ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]


OUTPUT_DIRECTORY = "./transcriptions"
INPUT_DIRECTORY = "./media"
EXPORT_FORMAT = "srt"


class TranscriptOptions(TypedDict):
    device: Literal["cpu", "gpu"]
    compute_type: str
    model_size_or_path: ModelSize
    cpu_threads : int


def get_arguments(args: List[str]) -> TranscriptOptions:
    """
    Given the CLI arguments returns the options to run the transcription
    """

    parser = argparse.ArgumentParser(
        description="Transcript audio/video files to wished format using Whisper"
    )

    parser.add_argument("--cuda", action="store_true", help="Use CUDA if available")
    parser.add_argument(
        "--model",
        default="tiny",
        choices=MODELS_OPTIONS,
        help=f"Model size (default: tiny), options {', '.join(MODELS_OPTIONS)}",
    )
    
    parser.add_argument("--cpu-threads", default=int((psutil.cpu_count(logical=True) or 8) / 2), 
                        choices=[str(pc) for pc in range(psutil.cpu_count()) if pc % 2 == 0],
                        help="Number of thread to assing to this transcription")

    parsed_args = parser.parse_args(args)

    options = vars(parsed_args)

    transcript_options = TranscriptOptions(
        compute_type="float16" if options.get("gpu") or options.get("cuda") else "int8",
        device="cuda" if options.get("cuda") or options.get("gpu") else "cpu",
        model_size_or_path=options["model"],
        cpu_threads = int(options["cpu_threads"])
    )

    return transcript_options

def run_transcription(selected_file: Path, options : TranscriptOptions):
    """
    Carrega as dependências pesadas e executa o processo de transcrição,
    usando uma barra de progresso do Rich.
    """
    # Inicializa o console do Rich para uma saída bonita
    console = Console()
    
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        console.print("[bold red]faster-whisper package not found, run ´uv´ to sync dependencies")
        sys.exit(1)

    try:
        console.print(
            f"\n🤖 Carregando modelo '[bold cyan]{options['model_size_or_path']}[/bold cyan]' ({options['device']})… usando cpu : {options['cpu_threads']}"
        )
        
        # Carregamento do modelo
        model = WhisperModel(
            options['model_size_or_path'],
            device=options['device'],
            compute_type=options['compute_type'],
            cpu_threads=options["cpu_threads"]
        )
        
    except Exception as e:
        console.print(f"❌ [bold red]Erro crítico ao carregar o modelo de IA:[/bold red] {e}")
        sys.exit(1)

    # Processo de transcrição
    console.print("🚀 [bold green]Iniciando transcrição...[/bold green]")
    segments, media_info = model.transcribe(str(selected_file), beam_size=5)

    show_media_info(info=media_info) # Você pode refatorar esta função para usar o console.print também

    temp_file = Path(f"{selected_file.stem}.tmp")

    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console
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
                    file_format=EXPORT_FORMAT,
                    index=idx, 
                    start_time=segment.start,
                )

                # Atualiza a barra de progresso, dizendo a ela em que ponto do tempo estamos.
                progress.update(transcription_task, completed=segment.end)

    # --- Finalização Segura ---
    destination_path = Path(OUTPUT_DIRECTORY) / f"{selected_file.stem}.{EXPORT_FORMAT}"
    try:
        temp_file.replace(destination_path)
        console.print(f"\n✅ [bold green]Transcrição salva com sucesso em:[/bold green] '{destination_path}'")
    except Exception as e:
        console.print(f"\n❌ [bold red]Erro ao salvar o ficheiro final:[/bold red] {e}")


def main() -> None:
    """
    The main function.
    """
    show_presentation()

    create_necessary_dirs(directories=[INPUT_DIRECTORY, OUTPUT_DIRECTORY])

    # organize media files sending it files to a common folder named: (INPUT_DIRECTORY)
    organize_files(input_dir=INPUT_DIRECTORY, output_dir=OUTPUT_DIRECTORY)

    # get  wanted file
    selected_file = select_file_prompt(
        files=get_valid_files(target_path=INPUT_DIRECTORY),
        output_folder=Path(OUTPUT_DIRECTORY),
    )
    
    run_transcription(selected_file=selected_file, options=get_arguments(sys.argv[1:]))

if __name__ == "__main__":
    try:
        main()
    except av.error.InvalidDataError:
        print("Arquivo selecionado esta corrompido ou não é valido")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n🍃🍃🍃 Saindo...")

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
from typing import List

import av.error
import psutil

from utils.io_tools import (
    create_necessary_dirs,
    get_valid_files,
    organize_files,
    select_file_prompt,
    save_transcription,
)
from utils.log_tools import (
    show_presentation,
)
from utils.transcript_tools import (
    MODELS_OPTIONS,
    RunTranscriptOptions,
    TranscriptOptions,
    run_transcription,
)

OUTPUT_DIRECTORY = "./transcriptions"
INPUT_DIRECTORY = "./media"
EXPORT_FORMAT = "srt"


def get_arguments(args : int):
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

    parser.add_argument(
        "--cpu-threads",
        default=int((psutil.cpu_count(logical=True) or 8) / 2),
        choices=[str(pc) for pc in range(psutil.cpu_count() or 2)],
        help="Number of thread to assing to this transcription",
    )

    parsed_args = parser.parse_args(args)

    options = vars(parsed_args)

    transcript_options = TranscriptOptions(
        compute_type="float16" if options.get("gpu") or options.get("cuda") else "int8",
        device="cuda" if options.get("cuda") or options.get("gpu") else "cpu",
        model_size_or_path=options["model"],
        cpu_threads=int(options["cpu_threads"]),
    )

    return transcript_options


def main() -> None:
    """
    The main function.
    """

    args = get_arguments(sys.argv[1:])

    show_presentation()

    create_necessary_dirs(directories=[Path(INPUT_DIRECTORY), Path(OUTPUT_DIRECTORY)])

    # organize media files sending it files to a common folder named: (INPUT_DIRECTORY)
    organize_files(input_dir=Path(INPUT_DIRECTORY), output_dir=Path(OUTPUT_DIRECTORY))

    # get  wanted file
    selected_files = select_file_prompt(
        files=get_valid_files(target_path=Path(INPUT_DIRECTORY)),
        output_folder=Path(OUTPUT_DIRECTORY),
    )

    from faster_whisper import WhisperModel

    model = WhisperModel(
        model_size_or_path=args.model_size_or_path,
        device=args.device,
        compute_type=args.compute_type,
        cpu_threads=args.cpu_threads,
    )

    for file in selected_files:
        params_for_transcription = RunTranscriptOptions(
            model=model,
            file=file,
        )

        segments = run_transcription(params=params_for_transcription)

        save_transcription(
            file=file,
            segments=segments,
            output_directory=Path(OUTPUT_DIRECTORY),
            export_fmt=EXPORT_FORMAT,
        )
    
    

if __name__ == "__main__":
    try:
        main()
    except av.error.InvalidDataError:
        print("Arquivo selecionado esta corrompido ou não é valido")
        sys.exit(1)

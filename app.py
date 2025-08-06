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

import sys
import argparse
from pathlib import Path
from typing import List, Literal, TypedDict
import av.error


MODELS_OPTIONS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")
ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]


OUTPUT_DIRECTORY = "./transcriptions"
INPUT_DIRECTORY = "./media"
EXPORT_FORMAT = "srt"


class TranscriptOptions(TypedDict):
    device: Literal["cpu", "gpu"]
    compute_type: str
    model_size_or_path: ModelSize


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

    parsed_args = parser.parse_args(args)

    options = vars(parsed_args)

    transcript_options = TranscriptOptions(
        compute_type="float16" if options.get("gpu") or options.get("cuda") else "gpu",
        device="cuda" if options.get("cuda") or options.get("gpu") else "cpu",
        model_size_or_path=options["model"],
    )

    return transcript_options


def main() -> None:
    """
    The main function.
    """

    from utils.log_tools import (
        show_presentation,
        show_media_info,
        show_transcript_status,
    )
    from utils.io_tools import (
        organize_files,
        get_valid_files,
        create_necessary_dirs,
        select_file_prompt,
    )

    show_presentation()

    create_necessary_dirs(directories=[INPUT_DIRECTORY, OUTPUT_DIRECTORY])

    # organize media files sending it files to a common folder named: (INPUT_DIRECTORY)
    organize_files(input_dir=INPUT_DIRECTORY, output_dir=OUTPUT_DIRECTORY)

    # get  wanted file
    selected_file = select_file_prompt(
        files=get_valid_files(target_path=INPUT_DIRECTORY),
        output_folder=Path(OUTPUT_DIRECTORY),
    )

    # getting config ------------------------------------
    options = get_arguments(sys.argv[1:])

    # Opening the model here, to dont slow down the initialization of the scritp ----------------
    try:
        print(
            f"\n🤖 Carregando modelo '{options['model_size_or_path']}' ({options['device']})…"
        )

        # Lazy import follwing the NFR-01
        from faster_whisper import WhisperModel

        model = WhisperModel(**options)
    except Exception as e:
        print(f"❌ Erro ao carregar modelo {e}")

    print("🚀 Iniciando transcrição")
    segs, media_info = model.transcribe(selected_file, beam_size=5)

    show_media_info(info=media_info)

    # Create temp file on Path vars
    temp_file = Path(f"{selected_file.stem}.tmp")
    from utils.transcript_tools import write_file, save_from_tmp_file

    with open(temp_file, "w", encoding="utf-8") as transcripted_file:
        for idx, segment in enumerate(segs):
            pct = (segment.end / media_info.duration) * 100

            show_transcript_status(data={"pct": pct, "segment": segment})

            # Write on file
            write_file(
                file=transcripted_file,
                content=segment.text,
                file_format=EXPORT_FORMAT,
                start_time=segment.start,
                end_time=segment.end,
                index=idx,
            )

    save_from_tmp_file(
        tmp=temp_file,
        file=selected_file,
        export_format=EXPORT_FORMAT,
        output_dir=OUTPUT_DIRECTORY,
    )


try:
    main()
except av.error.InvalidDataError:
    print("Arquivo selecionado esta corrompido ou não é valido")
    sys.exit(1)

except KeyboardInterrupt:
    print("\n🍃🍃🍃 Saindo...")

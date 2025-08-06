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

import os
import sys
import shutil
from pathlib import Path
from typing import List, Literal, TypedDict
import av.error
from math import ceil

from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo, Segment

MODELS_OPTIONS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")
ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]


OUTPUT_DIRECTORY = "./transcriptions"
INPUT_DIRECTORY = "./media"
EXPORT_FORMAT = "srt"


class TranscriptOptions(TypedDict):
    device: Literal["cpu", "gpu"]
    compute_type: str
    model_size_or_path: ModelSize

class TranscriptData(TypedDict):
    pct : str
    segment : Segment


VALID_FORMATS: List[str] = [
    "mp3",  # MPEG Audio
    "wav",  # Waveform Audio
    "m4a",  # MPEG-4 Audio (AAC)
    "mp4",  # MPEG-4 (pode conter vídeo, mas o áudio será extraído)
    "webm",  # Web Media
    "ogg",  # Ogg Vorbis
    "flac",  # Free Lossless Audio Codec
    "aac",  # Advanced Audio Coding
    "opus",  # Usado em Discord, WebRTC etc.
    "wma",  # Windows Media Audio
    "alac",  # Apple Lossless Audio Codec
    "aiff",  # Audio Interchange File Format
    "amr",  # Adaptive Multi-Rate (usado em celulares antigos)
    "3gp",  # Formato de vídeo/áudio em celulares, extrai o áudio
]


def get_valid_files(
    target_path: Path = Path("."), valid_formats: List[str] = None
) -> List[Path]:
    """
    This function analyze all the availables files on the target_path (param::)
    and return all the files on this among that are a valid based on valid format provided
    by the valid_formart (param::)

    params:
        - target_path : str ( path to the wished directory to be analized)
        - valid_formats : List[str] an array of valid formats that will make a file valid or not

    return :
        An array with the available files

    """
    # Keeping in 3 differents vars, but it can be in only one
    filtered_files: List[str] = [
        file
        for file in Path(target_path or INPUT_DIRECTORY).iterdir()
        if file.is_file()
        and not file.name.startswith((".", ","))
        and file.suffix.lstrip(".").lower() in valid_formats
    ]

    return filtered_files


def select_file_prompt(files: list[Path]) -> Path:
    """
    Show an input prompt showing all the file that can be
    transcripted, user need to select one

    params:
        - files : a array with all the available files to be transcripted

    return: str | path (the filename of selected file)
    """

    print("📁 Escolha o arquivo que voce deseja transcrever, use o numero do indice: ")
    print("-" * 50)

    def user_confirm_transcription():
        print(
            "This file apperentaly have been already transcripted do you want to proceed?"
        )

        try:
            input("Enter to proceed; cltr + c to cancel... ")
        except KeyboardInterrupt:
            print("Ignorando...")
            return False

        return True

    transcripted_files_in_output_dir = { f.stem for f in Path(OUTPUT_DIRECTORY).iterdir() }
    
    status_map = { file : file.stem in transcripted_files_in_output_dir for file in files }

    while True:

        for _, filename in enumerate(files):
            print(
                f"[{_}] - {filename.name} {'[Transcripted 📄]' if status_map[filename] else ''} 📂"
            )

        user_input = input("☑️  Escolha o arquivo: ")

        try:
            # Build the path to file
            result = files[int(user_input)]

            if status_map[result]:
                if user_confirm_transcription():
                    return result
                else:
                    continue
            return result

        except ValueError:
            sys.stdout.flush()
            print("❌ Digite apenas numeros...")
        except IndexError:
            sys.stdout.flush()
            print("\r❌ Escolha apenas os arquivos listados...")


def get_options(args: List[str]) -> TranscriptOptions:
    """
    Given the CLI arguments returns the options to run the transcription
    """

    options: TranscriptOptions = {
        "device": "cpu",
        "model_size_or_path": "medium",
        "compute_type": "int8",
    }

    # Check for GPU/CUDA usage
    if "--gpu" in args or "--cuda" in args:
        options["device"] = "cuda"
        options["compute_type"] = "float16"

    for arg in args:
        if arg.startswith("--model="):
            model = arg.split("=")[1]
            if model in MODELS_OPTIONS:
                options["model_size_or_path"] = model
                print(f"🤖 Usando modelo: {model}")

            else:
                print(f"❌ Modelo '{model}' não é válido.")
                print(f"🔎 Modelos válidos: {', '.join(MODELS_OPTIONS)}")
                sys.exit(1)

    return options


def send_valid_files_to_input_folder():
    """
    ATTENTION: NON-COMPONENTIBLE function, use just here in this software.
    The porpouse of this function make it just suitable for this scope.
    It depends exclusively on the INPUT_DIRECTORY and actual root directory

    This functio aim to get all valid files available in the root folder and move to
    an appropiated folder (INPUT_DIRECTORY)

    It applies changes on how user select files, that function need to ensure the file path is completed
    like media/audio.mp3 instead just audio.mp3
    """
    files = get_valid_files(target_path=Path("."), valid_formats=VALID_FORMATS)

    if len(files) == 0:
        return

    operation_log = {"moved_files": 0, "ignored_files": 0}

    for file in files:
        if Path(OUTPUT_DIRECTORY, file).exists():
            operation_log["ignored_files"] += 1
            continue

        shutil.move(file, INPUT_DIRECTORY)
        operation_log["moved_files"] += 1

    # the following lines adress to build a resume text to show what this operation did

    moved_files_text = f"{operation_log['moved_files']} arquivos movidos ➡️ para a pasta {INPUT_DIRECTORY} \n"
    ignored_files_text = f"{operation_log['ignored_files']} arquivos ignorados ❌ (ja existiam na pasta) {INPUT_DIRECTORY} \n"

    resume_text = "Uma operação organizacional foi concluida: \n"

    if operation_log["moved_files"]:
        resume_text += moved_files_text
    if operation_log["ignored_files"]:
        resume_text += ignored_files_text

    print(resume_text)


def check_if_file_already_transcripted(file: Path, files_output: List[Path]):
    """
    This function intend to check if a file have been transcripted already

    This function shall take the filename, remove extension, for instance:
    'audio.mp3' should result in 'audio' and then check if this ('audio' + '.' + EXPORT_FORMAT) for example:
        EXPORT_FORMAT = srt;
        expected_filename_in_output_directory -> (audio.srt)
    already exist in the OUTPUT_DIRECTORY

    params:
        - filename : the target filename
    """
    return file.stem in {file.stem for file in files_output}


def show_presentation():
    """Show software presentation on terminal"""

    # Presentation
    os.system("cls" if os.name == "nt" else "clear")
    print("🎤 Transcritor de Áudio/Vídeo para Legendas")
    print("=" * 50)


def create_necessary_dirs():
    # Create input folder
    os.makedirs(INPUT_DIRECTORY, exist_ok=True)

    # Create transcription folder
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def show_media_info(info: TranscriptionInfo):
    # Information about file, language and duration
    print(f"🌐 Detected language: {info.language}")
    print(f"📼 Duração da mídia: {info.duration / 60:.2f}m")


def show_transcript_status(data : TranscriptData):
    from utils import TerminalTools as TT

    # Terminal tools
    TT.clear_terminal_line()
    bar_text = f"[{'|' * ceil(ceil(data["pct"]) / 10)}{' ' * ceil((100 - ceil(data["pct"])) / 10)}]"
    msg = f"[ Progress: {ceil(data["pct"])}% ] - Transcription: {data["segment"].text[:40]}..."
    sys.stdout.write("\r" + bar_text + " " + msg)
    sys.stdout.flush()


def main() -> None:
    """
    The main function.
    """
 
    show_presentation()

    create_necessary_dirs()

    # organize media files sending it files to a common folder named: (INPUT_DIRECTORY)
    send_valid_files_to_input_folder()

    # Fetch all possible files to transcript on files inside the INPUT_DIRECTORY
    input_dir_valid_files = get_valid_files(
        target_path=INPUT_DIRECTORY, valid_formats=VALID_FORMATS
    )

    # If no files detected on INPUT_DIRECTORY, close the script and log some help
    if len(input_dir_valid_files) == 0:
        print(
            f"❌ Nenhum arquivo disponivel para transcrição.\nConsidere adicionar arquivos nos formatos compativeis. Verifique se voce adicionou arquivos a pasta atual {INPUT_DIRECTORY}"
        )
        sys.exit(1)

    # get  wanted file
    selected_file = select_file_prompt(files=input_dir_valid_files)
    
    # getting config ------------------------------------
    options = get_options(sys.argv)

    # Opening the model here, to dont slow down the initialization of the scritp ----------------
    try:
        print(f"\n🤖 Carregando modelo '{options['model_size_or_path']}' ({options['device']})…")
        model = WhisperModel(**options)
    except Exception as e:
        print(f"❌ Erro ao carregar modelo {e}")
        

    print("🚀 Iniciando transcrição")
    segs, media_info = model.transcribe(selected_file, beam_size=5)

    show_media_info(info=media_info)

    # Create temp file on Path vars
    temp_file = Path(f"{selected_file.stem}.tmp")
    with open(temp_file, "w", encoding="utf-8") as transcripted_file:
        for _, segment in enumerate(segs):
            pct = (segment.end / media_info.duration) * 100

            show_transcript_status( data = {
                "pct" : pct,
                "segment" : segment
            })

            # Write on file
            transcripted_file.write(
                f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text} \n"
            )
            
    # Resigning the file name from temp filename to final version filename
    final_filename = Path(f"{selected_file.stem}" + "." + EXPORT_FORMAT)
    
    destination_path = Path(OUTPUT_DIRECTORY) / final_filename
    
    try:
        temp_file.replace(destination_path)
    except Exception as e:
        print(f"❌ Erro ao processar transcrição: {e}")


try:
    main()
except av.error.InvalidDataError:
    print("Arquivo selecionado esta corrompido ou não é valido")
    sys.exit(1)

except KeyboardInterrupt:
    print("\n🍃🍃🍃 Saindo...")

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
from typing import List, Literal, TypedDict
import av.error
from datetime import datetime

from faster_whisper import WhisperModel

MODELS_OPTIONS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")
ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]


class TranscriptOptions(TypedDict):
    device: Literal["cpu", "gpu"]
    compute_type: str
    model_size_or_path: ModelSize


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


def get_valid_files() -> List[str]:
    """
    This function analyze all the availables files on the actual directory
    and return all the files on this among that are a valid transcriptable file, such as,
    audio, videos and other compatibles formats.

    params: None

    return :
        An array with the available files

    """
    # Keeping in 3 differents vars, but it can be in only one
    all_files: List[str] = [file for file in os.listdir() if not os.path.isdir(file)]
    non_hidden_all_files: List[str] = [
        file for file in all_files if not file.startswith((".", "_"))
    ]

    # The filenames of all available files transcrible
    valid_files: List[str] = []

    # Checking valid file formats
    for file in non_hidden_all_files:
        if file_type := file.split(".")[-1]:
            if file_type in VALID_FORMATS:
                valid_files.append(file)

    return valid_files


def select_file_prompt(files: list[str]) -> str:
    """
    Show an input prompt showing all the file that can be
    transcripted, user need to select one

    params:
        - files : a array with all the available files to be transcripted

    return: str | path (the filename of selected file)
    """

    if not files:
        print(
            "❌ Nenhum arquivo disponivel para transcrição.\nConsidere adicionar arquivos nos formatos compativeis."
        )
        sys.exit(1)

    print("📁 Escolha o arquivo que voce deseja transcrever, use o numero do indice: ")
    print("-" * 50)

    while True:
        for _, filename in enumerate(files):
            print(f"[{_}] - {filename} 📂")

        user_input = input("☑️  Escolha o arquivo: ")

        try:
            return files[int(user_input)]
        except ValueError:
            sys.stdout.flush()
            print("❌ Digite apenas numeros...")
        except IndexError:
            sys.stdout.flush()
            print("\r❌ Indice digitado nao é valido...")


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


def main() -> None:
    """
    The main function.
    """
    #Presentation
    os.system("cls" if os.name == "nt" else "clear")
    print("🎤 Transcritor de Áudio/Vídeo para Legendas")
    print("=" * 50)
    
    # Set up
    # Fetch all possible files to transcript
    valid_files = get_valid_files()

    # Select the wanted file
    file_name = select_file_prompt(files=valid_files)

    # Opening the model here, to dont slow down the initialization of the scritp
    model = WhisperModel(**get_options(sys.argv))

    segs, info = model.transcribe(file_name, beam_size=5)
    # Information about file, language and duration
    print(f"🌐 Detected language: {info.language}")
    print(f"📼 Duração da mídia: {info.duration}")

    TEMP_PATH = f"{file_name.split('.')[0]}.srt.tmp"
    FINAL_PATH = f"{file_name.split('.')[0]}.srt"

    with open(TEMP_PATH, "w", encoding="utf-8") as transcripted_file:
        time_start = datetime.now()
        for _, segment in enumerate(segs):
            pct = (segment.end / info.duration) * 100
            sys.stdout.write(f"\rProgress: {pct:.2f}% - Text: {segment.text[:40]}...\n")
            sys.stdout.flush()
            transcripted_file.write(
                f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text} \n"
            )
        finish_time = datetime.now()
        
        print(f"running time: {finish_time - time_start}")
    # Resigning the file name from temp filename to final version filename
    os.rename(TEMP_PATH, FINAL_PATH)



 
try:
    main()
except av.error.InvalidDataError:
    print("Arquivo selecionado esta corrompido ou não é valido")
    sys.exit(1)

except KeyboardInterrupt:
    print("\n🍃🍃🍃 Saindo...")

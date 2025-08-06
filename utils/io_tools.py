from pathlib import Path
from typing import List

import sys


from rich.console import Console

console = Console()

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


def organize_files(input_dir: Path, output_dir: Path):
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
        if Path(output_dir, file).exists():
            operation_log["ignored_files"] += 1
            continue

        file.replace(Path(input_dir) / file.name)

        operation_log["moved_files"] += 1

    # LOG OPERTATION ----------------------------------------------
    moved_files_text = (
        f"{operation_log['moved_files']} arquivos movidos ➡️ para a pasta {input_dir} \n"
    )
    ignored_files_text = f"{operation_log['ignored_files']} arquivos ignorados ❌ (ja existiam na pasta) {output_dir} \n"

    resume_text = "Uma operação organizacional foi concluida: \n"

    if operation_log["moved_files"]:
        resume_text += moved_files_text
    if operation_log["ignored_files"]:
        resume_text += ignored_files_text

    print(resume_text)


def get_valid_files(
    target_path: Path = Path("."),
    valid_formats=VALID_FORMATS,
    input_dir: Path = Path("."),
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
        for file in Path(target_path or input_dir).iterdir()
        if file.is_file()
        and not file.name.startswith((".", ","))
        and file.suffix.lstrip(".").lower() in valid_formats
    ]

    return filtered_files


def create_necessary_dirs(directories: List[Path]):
    # Create input folder
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def select_file_prompt(files: list[Path], output_folder: Path) -> Path:
    """
    Show an input prompt showing all the file that can be
    transcripted, user need to select one

    params:
        - files : a array with all the available files to be transcripted

    return: str | path (the filename of selected file)
    """

    import questionary

    console.print(
        "📁 [bold green] Escolha o arquivo que voce deseja transcrever, use o numero do indice: "
    )
    console.print("[bold yellow]-" * 50)

    def user_confirm_prompt():
        console.print(
            " ⚠️ [bold yellow] This file have been already transcripted do you want to proceed?"
        )
        return questionary.confirm("Deseja prosseguir?").ask()

    # All files inside the OUTPUT_DIRECTORY
    transcripted_files_in_output_dir = {
        transcripted_file.stem for transcripted_file in output_folder.iterdir()
    }

    # For each file we create a indice on this to mark if file was transcripted or not
    status_map = {
        file: (file.stem in transcripted_files_in_output_dir) for file in files
    }

    files_for_menu = []

    for file in files:
        files_for_menu.append(questionary.Choice(title=f"{file.name} [Transcripted]" if status_map[file] else file.name, value=file, description=file))

    while True:
        selected_file = questionary.select(
            "Selecione o arquivo que voce deseja transcrever: ",
            choices=files_for_menu,
            show_description=True,
            instruction="Use as setas do teclado",
            use_shortcuts=True,
        ).unsafe_ask()
        
        if selected_file:
            return selected_file

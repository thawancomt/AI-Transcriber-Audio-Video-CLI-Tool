from _io import TextIOWrapper
from pathlib import Path
from typing import List, Iterator, Literal

from rich.console import Console
from faster_whisper.transcribe import Segment

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
    valid_formats: List[str] = VALID_FORMATS,
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
    filtered_files: List[Path] = [
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


def select_file_prompt(files: list[Path], output_folder: Path) -> List[Path]:
    """
    Show an input prompt showing all the file that can be
    transcripted, user need to select one

    params:
        - files : a array with all the available files to be transcripted

    return: List[path] (List of selected file path)
    """

    import questionary

    console.print(
        "📁 [bold green] Choose files to be transcripted: "
    )
    console.print("[bold yellow]-" * 50)

    def user_confirm_prompt():
        console.print(
            "⚠️ [bold yellow] One or more selected files have already been transcripted"
        )
        console.print("=" * 50)
        return questionary.confirm("Do you wanna proceed with operation?").ask()

    # All files inside the OUTPUT_DIRECTORY
    transcripted_files_in_output_dir = {
        transcripted_file.stem for transcripted_file in output_folder.iterdir()
    }

    # For each file we create a indice on this to mark if file was transcripted or not
    status_map = {
        file: (file.stem in transcripted_files_in_output_dir) for file in files
    }

    ALL_FILES  = "__ALL__"
    choices_for_menu: List[questionary.Choice] = [
        questionary.Choice("All available files", ALL_FILES, description="Select all available files",)
    ]

    for file in files:
        choices_for_menu.append(
            questionary.Choice(
                title=f"{file.name} [Transcripted]" if status_map[file] else file.name,
                value=file,
                description=str(file),
            )
        )

    while True:
        selected_files = questionary.checkbox(
            message="Select files to transcribe:",
            choices=choices_for_menu,
        ).unsafe_ask()

        if selected_files:
            if any((file.value in status_map) for file in choices_for_menu):
                import os
                os.system("clear" if os.name == "posix" else "cls")
                if user_confirm_prompt():
                    pass
                else:
                    continue
        else:
            console.print("⚠️ [bold red] You need to to select at least one file")
            continue

        return selected_files if ALL_FILES not in selected_files else files


def _write_srt(
    file: TextIOWrapper, index: int, start_time: float, end_time: float, content: str
):
    """"""
    text = f"""{index}\n{start_time} --> {end_time}\n{content}\n\n"""
    file.write(text)


def _write_txt(file: TextIOWrapper, content: str):
    """Write on txt files"""
    file.write(content)
    return file


def write_file(
    file: TextIOWrapper,
    content: str,
    start_time: float,
    end_time: float,
    index: int = 0,
    file_format: str = "txt",
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


def save_transcription(
    file: Path,
    segments: Iterator[Segment],
    output_directory: Path,
    export_fmt: Literal["txt", "srt"],
):
    temp_file = Path(output_directory / f"{file.stem}.tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, 1):
            write_file(
                file=f,
                content=seg.text,
                end_time=seg.end,
                file_format="srt",
                index=idx,
                start_time=seg.start,
            )
        f.close()

    final_file = Path(output_directory / f"{file.stem}{(f'.{export_fmt}')}")

    try:
        temp_file.replace(final_file)
    except FileNotFoundError as e:
        console.print(
            "[bold red] It was not possible to save the file, more details: ", e
        )
    except Exception as e:
        console.print(
            f"[bold red] An error occour while saving file on output_folder [bold white]({output_directory})[bold red], see: \n{e}"
        )

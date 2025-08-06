from _io import TextIOWrapper
from pathlib import Path

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

def save_from_tmp_file(tmp : Path, file : Path, export_format : str, output_dir):
    # Resigning the file name from temp filename to final version filename
    final_filename = Path(f"{file.stem}" + "." + export_format)

    destination_path = Path(output_dir) / final_filename

    try:
        tmp.replace(destination_path)
    except Exception as e:
        print(f"❌ Erro ao processar transcrição: {e}")
        

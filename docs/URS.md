This document intend to list all user requirements:

# On user pespective this software need to do:

legend:
`UR` stands for `user requirement`

- `UR-1`  The user must be able to choose which file will be transcripted (interactively)
- `UR-2`  The user must be able to select if the transcription process will use GPU device (CUDA) or CPU (default)
- `UR-3`  The user must be able to visualize the actual process step on the script throught logs on terminal (Real Time)
- `UR-4` Transcript all common media file format, such as :
    - mp3
    - mp4
    - flac
    - opus
    - webm
    - ogg
    - aac
- `UR-5` The transcripted text need to be saved in a SRT file with the same name of the base filename (excluding the extension, like `mp4`, `mp3`).
- `UR-6` The user must be able to select which type of model will be used to transcript user´s files.
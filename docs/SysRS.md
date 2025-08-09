Regardly URS (user requirements specification) this document intend to list
what is need to meet the requirements

Based on USR, this software need to implement a algorytimh that transcript audio/video files and save to a SRT file.

legend:
`FR` stands for `functional requirement`
`NFR` stands for `non-functional requirement`

The software must:
- `FR-1` (Ref. `UR-1`): This software shall implement a algorithm that analyze valid files in the current script directory and let the user to determine which media will be transcripted in a interactive way

- `FR-2` (Ref. `UR-2`): This software must be able to take advantage of specialized devices, such as `GPU` (`CUDA devices`), but by default need to run on `CPU`

- `FR-3` (Ref. `FR-2`): To meet the `FR-2` requirement, this software needs to be flexible to accept args to flow this software how to proceed in the transcription process, for example, which type of hardware device need to be used or max-timeout...

- `FR-4` (Ref. `UR-6`): This software need to provide different options of models used to transcript user's media files, fo instance, a `minimum-model` specialized on simple transcript or a `heavy-model` that use a more complex vocabulary and understanding capacity to infer what is been transcripted.

- `FR-5` (Ref. `UR-5`): This software must be able to save the transcripted text into a file, allegedly a SRT file, that was the format choosen according to `UR-5`.

- `FR-6` (Ref. `UR-7`): The software shall implement a way to user select multimple file at once.

Non-Functional Requirements (NFR):

- `NFR-01` (Performance): This software must initialize no longer than 15 seconds on low-end pc, and 8 seconds on high-end pcs, implementing technicques like, lazy process, lazy import methods

- `NFR-02` (Usability): This software need to explicity the errors to user, such as, listing the reasons of why an error occoured, like, `No files founds`, `Incompatible device`

- `NFR-03` (Compatibility): This software need to be able to run on diffent types of `OS`, such as, Windows, Linux or MacOS.
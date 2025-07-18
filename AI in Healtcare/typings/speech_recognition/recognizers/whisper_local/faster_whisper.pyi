"""
This type stub file was generated by pyright.
"""

import numpy as np
from typing import Literal, TYPE_CHECKING, TypedDict
from speech_recognition.audio import AudioData
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from typing_extensions import Unpack

if TYPE_CHECKING:
    ...
class TranscribeOutput(TypedDict):
    text: str
    segments: list[Segment]
    language: str
    ...


class TranscribableAdapter:
    def __init__(self, model: WhisperModel) -> None:
        ...
    
    def transcribe(self, audio_array: np.ndarray, **kwargs) -> TranscribeOutput:
        ...
    


class InitOptionalParameters(TypedDict, total=False):
    device: Literal["cpu", "gpu", "auto"]
    compute_type: str
    download_root: str
    ...


class TranscribeOptionalParameters(TypedDict, total=False):
    language: str
    task: Literal["transcribe", "translate"]
    beam_size: int
    ...


def recognize(recognizer, audio_data: AudioData, model: str = ..., show_dict: bool = ..., init_options: InitOptionalParameters | None = ..., **transcribe_options: Unpack[TranscribeOptionalParameters]) -> str | TranscribeOutput:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using Whisper.

    Pick ``model`` size (Same as Whisper).

    If ``show_dict`` is true, returns the detailed response from Whisper, including the detected language. Otherwise returns only the transcription.

    You can specify:

        * ``language``: recognition language, an uncapitalized 2 letters language name like "en" or "fr".

            * If not set, Faster Whisper will automatically detect the language.

        * ``task``

            * If you want transcribe + **translate** to english, set ``task="translate"``.

    Other values are passed directly to whisper. See https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py for all options.
    """
    ...

if __name__ == "__main__":
    parser = ...
    args = ...
    audio_data = ...
    transcription = ...
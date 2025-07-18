"""
This type stub file was generated by pyright.
"""

import aifc
import audioop
import base64
import collections
import hashlib
import hmac
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import wave
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .audio import AudioData, get_flac_converter
from .exceptions import RequestError, TranscriptionFailed, TranscriptionNotReady, UnknownValueError, WaitTimeoutError
from .recognizers import google, google_cloud, pocketsphinx
from .recognizers.whisper_api import groq, openai
from .recognizers.whisper_local import faster_whisper, whisper

"""Library for performing speech recognition, with support for several engines and APIs, online and offline."""
__author__ = ...
__version__ = ...
__license__ = ...
class AudioSource:
    def __init__(self) -> None:
        ...
    
    def __enter__(self):
        ...
    
    def __exit__(self, exc_type, exc_value, traceback):
        ...
    


class Microphone(AudioSource):
    """
    Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.

    This will throw an ``AttributeError`` if you don't have PyAudio (0.2.11 or later) installed.

    If ``device_index`` is unspecified or ``None``, the default microphone is used as the audio source. Otherwise, ``device_index`` should be the index of the device to use for audio input.

    A device index is an integer between 0 and ``pyaudio.get_device_count() - 1`` (assume we have used ``import pyaudio`` beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the `PyAudio documentation <http://people.csail.mit.edu/hubert/pyaudio/docs/>`__ for more details.

    The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz). If not specified, the value of ``sample_rate`` is determined automatically from the system's microphone settings.

    Higher ``sample_rate`` values result in better audio quality, but also more bandwidth (and therefore, slower recognition). Additionally, some CPUs, such as those in older Raspberry Pi models, can't keep up if this value is too high.

    Higher ``chunk_size`` values help avoid triggering on rapidly changing ambient noise, but also makes detection less sensitive. This value, generally, should be left at its default.
    """
    def __init__(self, device_index=..., sample_rate=..., chunk_size=...) -> None:
        ...
    
    @staticmethod
    def get_pyaudio(): # -> Any:
        """
        Imports the pyaudio module and checks its version. Throws exceptions if pyaudio can't be found or a wrong version is installed
        """
        ...
    
    @staticmethod
    def list_microphone_names(): # -> list[Any]:
        """
        Returns a list of the names of all available microphones. For microphones where the name can't be retrieved, the list entry contains ``None`` instead.

        The index of each microphone's name in the returned list is the same as its device index when creating a ``Microphone`` instance - if you want to use the microphone at index 3 in the returned list, use ``Microphone(device_index=3)``.
        """
        ...
    
    @staticmethod
    def list_working_microphones(): # -> dict[Any, Any]:
        """
        Returns a dictionary mapping device indices to microphone names, for microphones that are currently hearing sounds. When using this function, ensure that your microphone is unmuted and make some noise at it to ensure it will be detected as working.

        Each key in the returned dictionary can be passed to the ``Microphone`` constructor to use that microphone. For example, if the return value is ``{3: "HDA Intel PCH: ALC3232 Analog (hw:1,0)"}``, you can do ``Microphone(device_index=3)`` to use that microphone.
        """
        ...
    
    def __enter__(self): # -> Self:
        ...
    
    def __exit__(self, exc_type, exc_value, traceback): # -> None:
        ...
    
    class MicrophoneStream:
        def __init__(self, pyaudio_stream) -> None:
            ...
        
        def read(self, size):
            ...
        
        def close(self): # -> None:
            ...
        
    
    


class AudioFile(AudioSource):
    """
    Creates a new ``AudioFile`` instance given a WAV/AIFF/FLAC audio file ``filename_or_fileobject``. Subclass of ``AudioSource``.

    If ``filename_or_fileobject`` is a string, then it is interpreted as a path to an audio file on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar.

    Note that functions that read from the audio (such as ``recognizer_instance.record`` or ``recognizer_instance.listen``) will move ahead in the stream. For example, if you execute ``recognizer_instance.record(audiofile_instance, duration=10)`` twice, the first time it will return the first 10 seconds of audio, and the second time it will return the 10 seconds of audio right after that. This is always reset to the beginning when entering an ``AudioFile`` context.

    WAV files must be in PCM/LPCM format; WAVE_FORMAT_EXTENSIBLE and compressed WAV are not supported and may result in undefined behaviour.

    Both AIFF and AIFF-C (compressed AIFF) formats are supported.

    FLAC files must be in native FLAC format; OGG-FLAC is not supported and may result in undefined behaviour.
    """
    def __init__(self, filename_or_fileobject) -> None:
        ...
    
    def __enter__(self): # -> Self:
        ...
    
    def __exit__(self, exc_type, exc_value, traceback): # -> None:
        ...
    
    class AudioFileStream:
        def __init__(self, audio_reader, little_endian, samples_24_bit_pretending_to_be_32_bit) -> None:
            ...
        
        def read(self, size=...): # -> bytes:
            ...
        
    
    


class Recognizer(AudioSource):
    def __init__(self) -> None:
        """
        Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.
        """
        ...
    
    def record(self, source, duration=..., offset=...): # -> AudioData:
        """
        Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

        If ``duration`` is not specified, then it will record until there is no more audio input.
        """
        ...
    
    def adjust_for_ambient_noise(self, source, duration=...): # -> None:
        """
        Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.

        Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.

        The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.
        """
        ...
    
    def snowboy_wait_for_hot_word(self, snowboy_location, snowboy_hot_word_files, source, timeout=...): # -> tuple[bytes, Any]:
        ...
    
    def listen(self, source, timeout=..., phrase_time_limit=..., snowboy_configuration=..., stream=...): # -> AudioData | Generator[AudioData, Any, None]:
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

        If the ``stream`` keyword argument is ``True``, the ``listen()`` method will yield ``AudioData`` instances representing chunks of audio data as they are detected. The first yielded ``AudioData`` instance represents the first buffer of the phrase, and the last yielded ``AudioData`` instance represents the last buffer of the phrase. If ``stream`` is ``False``, the method will return a single ``AudioData`` instance representing the entire phrase.

        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.

        The ``timeout`` parameter is the maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.

        The ``phrase_time_limit`` parameter is the maximum number of seconds that this will allow a phrase to continue before stopping and returning the part of the phrase processed before the time limit was reached. The resulting audio will be the phrase cut off at the time limit. If ``phrase_timeout`` is ``None``, there will be no phrase time limit.

        The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).

        This operation will always complete within ``timeout + phrase_timeout`` seconds if both are numbers, either by returning the audio data, or by raising a ``speech_recognition.WaitTimeoutError`` exception.
        """
        ...
    
    def listen_in_background(self, source, callback, phrase_time_limit=...): # -> Callable[..., None]:
        """
        Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.

        Returns a function object that, when called, requests that the background listener thread stop. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads. The function accepts one parameter, ``wait_for_stop``: if truthy, the function will wait for the background listener to stop before returning, otherwise it will return immediately and the background listener thread might still be running for a second or two afterwards. Additionally, if you are using a truthy value for ``wait_for_stop``, you must call the function from the same thread you originally called ``listen_in_background`` from.

        Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``. The ``phrase_time_limit`` parameter works in the same way as the ``phrase_time_limit`` parameter for ``recognizer_instance.listen(source)``, as well.

        The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that ``callback`` function will be called from a non-main thread.
        """
        ...
    
    def recognize_wit(self, audio_data, key, show_all=...): # -> Any:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Wit.ai API.

        The Wit.ai API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://wit.ai/>`__ and creating an app. You will need to add at least one intent to the app before you can see the API key, though the actual intent settings don't matter.

        To get the API key for a Wit.ai app, go to the app's overview page, go to the section titled "Make an API request", and look for something along the lines of ``Authorization: Bearer XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX``; ``XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`` is the API key. Wit.ai API keys are 32-character uppercase alphanumeric strings.

        The recognition language is configured in the Wit.ai app settings.

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://wit.ai/docs/http/20141022#get-intent-via-text-link>`__ as a JSON dictionary.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        ...
    
    def recognize_azure(self, audio_data, key, language=..., profanity=..., location=..., show_all=...): # -> Any | tuple[Any, Any]:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Microsoft Azure Speech API.

        The Microsoft Azure Speech API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://azure.microsoft.com/en-ca/pricing/details/cognitive-services/speech-api/>`__ with Microsoft Azure.

        To get the API key, go to the `Microsoft Azure Portal Resources <https://portal.azure.com/>`__ page, go to "All Resources" > "Add" > "See All" > Search "Speech > "Create", and fill in the form to make a "Speech" resource. On the resulting page (which is also accessible from the "All Resources" page in the Azure Portal), go to the "Show Access Keys" page, which will have two API keys, either of which can be used for the `key` parameter. Microsoft Azure Speech API keys are 32-character lowercase hexadecimal strings.

        The recognition language is determined by ``language``, a BCP-47 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English. A list of supported language values can be found in the `API documentation <https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoicerecognition#recognition-language>`__ under "Interactive and dictation mode".

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoicerecognition#sample-responses>`__ as a JSON dictionary.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        ...
    
    def recognize_bing(self, audio_data, key, language=..., show_all=...): # -> Any:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Microsoft Bing Speech API.

        The Microsoft Bing Speech API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://azure.microsoft.com/en-ca/pricing/details/cognitive-services/speech-api/>`__ with Microsoft Azure.

        To get the API key, go to the `Microsoft Azure Portal Resources <https://portal.azure.com/>`__ page, go to "All Resources" > "Add" > "See All" > Search "Bing Speech API > "Create", and fill in the form to make a "Bing Speech API" resource. On the resulting page (which is also accessible from the "All Resources" page in the Azure Portal), go to the "Show Access Keys" page, which will have two API keys, either of which can be used for the `key` parameter. Microsoft Bing Speech API keys are 32-character lowercase hexadecimal strings.

        The recognition language is determined by ``language``, a BCP-47 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English. A list of supported language values can be found in the `API documentation <https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoicerecognition#recognition-language>`__ under "Interactive and dictation mode".

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoicerecognition#sample-responses>`__ as a JSON dictionary.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        ...
    
    def recognize_lex(self, audio_data, bot_name, bot_alias, user_id, content_type=..., access_key_id=..., secret_access_key=..., region=...):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Amazon Lex API.

        If access_key_id or secret_access_key is not set it will go through the list in the link below
        http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
        """
        ...
    
    def recognize_houndify(self, audio_data, client_id, client_key, show_all=...): # -> Any | tuple[Any, Any]:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Houndify API.

        The Houndify client ID and client key are specified by ``client_id`` and ``client_key``, respectively. Unfortunately, these are not available without `signing up for an account <https://www.houndify.com/signup>`__. Once logged into the `dashboard <https://www.houndify.com/dashboard>`__, you will want to select "Register a new client", and fill in the form as necessary. When at the "Enable Domains" page, enable the "Speech To Text Only" domain, and then select "Save & Continue".

        To get the client ID and client key for a Houndify client, go to the `dashboard <https://www.houndify.com/dashboard>`__ and select the client's "View Details" link. On the resulting page, the client ID and client key will be visible. Client IDs and client keys are both Base64-encoded strings.

        Currently, only English is supported as a recognition language.

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        ...
    
    def recognize_amazon(self, audio_data, bucket_name=..., access_key_id=..., secret_access_key=..., region=..., job_name=..., file_key=...): # -> tuple[Any, float]:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance) using Amazon Transcribe.
        https://aws.amazon.com/transcribe/
        If access_key_id or secret_access_key is not set it will go through the list in the link below
        http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
        """
        ...
    
    def recognize_assemblyai(self, audio_data, api_token, job_name=..., **kwargs): # -> tuple[Any, Any]:
        """
        Wraps the AssemblyAI STT service.
        https://www.assemblyai.com/
        """
        ...
    
    def recognize_ibm(self, audio_data, key, language=..., show_all=...): # -> Any | tuple[LiteralString, Any | None]:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the IBM Speech to Text API.

        The IBM Speech to Text username and password are specified by ``username`` and ``password``, respectively. Unfortunately, these are not available without `signing up for an account <https://console.ng.bluemix.net/registration/>`__. Once logged into the Bluemix console, follow the instructions for `creating an IBM Watson service instance <https://www.ibm.com/watson/developercloud/doc/getting_started/gs-credentials.shtml>`__, where the Watson service is "Speech To Text". IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX, while passwords are mixed-case alphanumeric strings.

        The recognition language is determined by ``language``, an RFC5646 language tag with a dialect like ``"en-US"`` (US English) or ``"zh-CN"`` (Mandarin Chinese), defaulting to US English. The supported language values are listed under the ``model`` parameter of the `audio recognition API documentation <https://www.ibm.com/watson/developercloud/speech-to-text/api/v1/#sessionless_methods>`__, in the form ``LANGUAGE_BroadbandModel``, where ``LANGUAGE`` is the language value.

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://www.ibm.com/watson/developercloud/speech-to-text/api/v1/#sessionless_methods>`__ as a JSON dictionary.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        ...
    
    lasttfgraph = ...
    tflabels = ...
    def recognize_tensorflow(self, audio_data, tensor_graph=..., tensor_label=...): # -> None:
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance).

        Path to Tensor loaded from ``tensor_graph``. You can download a model here: http://download.tensorflow.org/models/speech_commands_v0.01.zip

        Path to Tensor Labels file loaded from ``tensor_label``.
        """
        ...
    
    def recognize_vosk(self, audio_data, language=...): # -> LiteralString:
        ...
    


class PortableNamedTemporaryFile:
    """Limited replacement for ``tempfile.NamedTemporaryFile``, except unlike ``tempfile.NamedTemporaryFile``, the file can be opened again while it's currently open, even on Windows."""
    def __init__(self, mode=...) -> None:
        ...
    
    def __enter__(self): # -> Self:
        ...
    
    def __exit__(self, exc_type, exc_value, traceback): # -> None:
        ...
    
    def write(self, *args, **kwargs): # -> int:
        ...
    
    def writelines(self, *args, **kwargs): # -> None:
        ...
    
    def flush(self, *args, **kwargs): # -> None:
        ...
    


WavFile = AudioFile
def recognize_api(self, audio_data, client_access_token, language=..., session_id=..., show_all=...): # -> Any:
    ...
from typing import Literal

import base64
import json

import io
import wave
import pyaudio

import requests

import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts import ResultCallback, SpeechSynthesizer, SpeechSynthesisResult


def play_audio_by_bytes(wav_bytes: bytes):
    p = pyaudio.PyAudio()
    with io.BytesIO(wav_bytes) as wav_file:
        with wave.open(wav_file, 'rb') as wf:
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
    p.terminate()


def get_module_lists(url):
    try:
        response = requests.post(f"{url}/get_module_lists")
    except requests.exceptions.ConnectionError:
        return {}
    if response.status_code != 200:
        return {}
    return response.json()


def change_module(name: str, module_info: dict, url):
    response = requests.post(
        f"{url}/change_module",
        json={"module_name": name, "module_info": module_info})
    return response.json()


def take_a_tts(text: str, language: Literal['zh', 'en', 'ja', 'ko', 'yue'], module_name: str, module_info: dict,
               top_k: int = 12, top_p: float = 0.95, temperature: float = 0.34, speed: float = 1.0,
               batch_size: int = 3, batch_threshold: float = 0.75,
               seed: int = -1, parallel_infer: bool = True, repetition_penalty: float = 1.35,
               url: str = ""):
    tts_param = {
        "text": text,
        "language": language,
        "module_name": module_name,
        "module_info": module_info,
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "speed": speed,
        "batch_size": batch_size,
        "batch_threshold": batch_threshold,
        "seed": seed,
        "parallel_infer": parallel_infer,
        "repetition_penalty": repetition_penalty
    }
    response = requests.post(f"{url}/take_tts", json=tts_param)
    return base64.b64decode(json.loads(response.json())['result'])


def ali_tts(text: str):
    result_voice: SpeechSynthesisResult | None = None

    class Callback(ResultCallback):
        def on_open(self):
            pass

        def on_complete(self):
            pass

        def on_error(self, response: SpeechSynthesisResponse):
            pass

        def on_close(self):
            pass

        def on_event(self, result: SpeechSynthesisResult):
            nonlocal result_voice
            result_voice = result

    callback = Callback()
    result = SpeechSynthesizer.call(model='sambert-zhiqi-v1',
                                    text=text,
                                    sample_rate=48000,
                                    format='wav',
                                    callback=callback,
                                    word_timestamp_enabled=True,
                                    )

    if result.get_audio_data() is not None:
        return result.get_audio_data(), int(result_voice.get_timestamp()['end_time'])
    return None, None

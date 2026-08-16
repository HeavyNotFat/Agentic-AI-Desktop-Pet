import asyncio
import base64
import json
import os
import tempfile
import wave
import time
import socket

import websockets
import whisper
import pyaudio

model = whisper.load_model("medium")
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

ip = socket.gethostbyname(socket.gethostname())
port = int(time.strftime("%Y")) + 3


async def recognize_audio(websocket):
    audio_data = bytearray()

    while True:
        message = await websocket.recv()
        print("[INFO] Received audio data")
        audio_data.extend(base64.b64decode(json.loads(message)['data']))
        wave_filename = f"{tempfile.gettempdir()}/output_{int(time.time())}.wav"
        save_audio(audio_data, wave_filename)
        result = model.transcribe(wave_filename)
        print(f"[INFO] Transcription completed, {result} at {wave_filename}")
        os.remove(wave_filename)
        await websocket.send(json.dumps({"text": result['text'], "language": result['language']}, ensure_ascii=False))
        print("[INFO] Sent message")
        audio_data.clear()


def save_audio(audio_data, filename):
    """
    保存成wav文件进行识别
    不要问我为什么，这样识别准一点……
    """
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()


async def start():
    """
    使用异步开启
    """
    print(f'[INFO] start WebSocket Server on ws://{ip}:{port}')
    async with websockets.serve(recognize_audio, ip, port):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("[INFO] Server has been stopped by user")

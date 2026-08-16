from urllib.parse import urlencode
import datetime
import hashlib
import json
from datetime import datetime
from time import mktime
import base64

import threading

import hmac
import ssl
from wsgiref.handlers import format_date_time

import numpy
import websocket
import pyaudio

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2
CHANNELS = 1
RATE = 16000
CHUNK = 1024

API_ID = ""
API_KEY = ""
API_SECRET = ""


class WhisperRealTimeSpeechRecognizer:
    """
    实时语音识别器，用于通过WebSocket连接到服务器进行语音识别。
    """

    def __init__(self, success_func, failure_func, close_func, ws_url, configure, save_func):
        """
        初始化实时语音识别器。
        """
        # 初始化变量
        self.is_continue = True
        self.ws_url = ws_url
        self.configure = configure
        self.save_func = save_func
        self.success_func = success_func
        self.failure_func = failure_func
        self.close_func = close_func

        # 初始化运行时样本次数和采样次数
        self.runtime_sample_times = self.sampled_times = 0
        # 初始化算法和进度函数
        self.algorithm = self.progress_func = None
        # 初始化是否开始采样标志
        self.is_started_sampling = False
        # 获取静音阈值和持续时间
        self.silence_threshold = self.configure['settings']['rec']['silence_threshold']
        self.silence_duration = RATE * self.configure['settings']['rec']['silence_duration']
        # 初始化静音样本和音频缓冲区
        self.silence_sample = []
        self.audio_buffer = []

    def on_message(self, ws, message):
        """
        处理WebSocket消息的函数。
        """
        # 调用成功回调函数处理识别结果，并清空音频缓冲区
        self.success_func(json.loads(message)['text'])
        self.audio_buffer = []

    def on_error(self, ws, error):
        """
        处理WebSocket错误的函数。
        """
        # 调用失败回调函数处理错误
        self.failure_func(ws, error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        处理WebSocket关闭连接的函数。
        """
        # 设置继续标志为False，并调用关闭回调函数
        self.is_continue = False
        self.close_func()

    def on_open(self, ws):
        """
        处理WebSocket打开连接的函数。
        """

        def run():
            # 初始化PyAudio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

            silence_counter = 0
            while self.is_continue:
                data = stream.read(CHUNK)
                if not data:
                    continue
                audio_data = numpy.frombuffer(data, dtype=numpy.int16).astype(numpy.float32) / 32768.0
                if self.silence_threshold is None:
                    self._compute_sample(audio_data)
                    continue
                if not self._is_silent(audio_data):
                    self.audio_buffer.append(data)
                    silence_counter = 0
                else:
                    silence_counter += CHUNK
                    if len(self.audio_buffer) > 0 and silence_counter >= self.silence_duration:
                        audio_to_send = base64.b64encode(b''.join(self.audio_buffer)).decode()
                        ws.send(json.dumps({"data": audio_to_send}))
                        self.audio_buffer = []

            stream.stop_stream()
            stream.close()
            p.terminate()
            ws.close()

        # 在新线程中运行
        threading.Thread(target=run).start()

    def compute_sample(self, algorithm: int, progress_func: callable, times: int):
        """
        计算样本。
        """
        # 初始化静音样本和采样次数
        self.silence_sample = []
        self.sampled_times = 0
        # 设置算法和进度函数
        self.algorithm = algorithm
        self.progress_func = progress_func
        self.runtime_sample_times = times
        # 设置静音阈值为None，表示开始自动采样
        self.silence_threshold = None
        self.is_started_sampling = True

    def _compute_sample(self, audio_data):
        """
        自动采样

        算法实用情况：
        0 -> 家庭无嘈杂
        1 -> 家庭有嘈杂
        2 -> 室外无噪音
        3 -> 地铁等高噪音
        """
        if not self.is_started_sampling:
            return
        # 根据算法计算当前阈值
        if len(self.silence_sample) > 0 and self.algorithm == 0:
            # 当算法为0时，当前阈值为静默样本的平均值
            current_threshold = numpy.mean(self.silence_sample)
        elif len(self.silence_sample) > 0 and self.algorithm == 1:
            # 当算法为1时，当前阈值为静默样本的平均值加上最小值
            current_threshold = numpy.mean(self.silence_sample) + min(self.silence_sample)
        elif len(self.silence_sample) > 0 and self.algorithm == 2:
            # 当算法为2时，当前阈值为静默样本的平均值加上最大值
            current_threshold = numpy.mean(self.silence_sample) + max(self.silence_sample)
        elif len(self.silence_sample) > 0 and self.algorithm == 3:
            # 当算法为3时，当前阈值为静默样本平均值的两倍
            current_threshold = numpy.mean(self.silence_sample) * 2
        else:
            # 当没有静默样本时，将当前阈值设为0
            current_threshold = 0
        if len(self.silence_sample) > self.runtime_sample_times:
            if self.silence_threshold is None:
                self.silence_threshold = current_threshold
                self.configure['settings']['rec']['silence_threshold'] = float(self.silence_threshold)
                self.save_func(self.configure)
                print(f"[AUTO COMPUTE] average: {self.silence_threshold}")
        if self.silence_threshold is None:
            # 计算并添加当前音频数据的响度到静默样本列表中
            self.silence_sample.append(numpy.sqrt(numpy.mean(numpy.square(audio_data))))
            self.sampled_times += 1
        self.progress_func(self.sampled_times - 1, current_threshold)

    def _is_silent(self, audio_data):
        """判断音频数据是否为静音"""
        # 简易计算RMS
        return numpy.sqrt(numpy.mean(numpy.square(audio_data))) < self.silence_threshold

    def closed(self):
        """关闭识别器"""
        self.is_continue = False

    def statued(self):
        """状态更新"""
        pass

    def start_recognition(self):
        """开始语音识别"""
        ws = websocket.WebSocketApp(self.ws_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

        ws.run_forever()


class XFRealTimeSpeechRecognizer:
    def __init__(self, success_func, error_func, close_func, *args):
        self.is_status = False
        self.is_continue = True
        self.success_func = success_func
        self.error_func = error_func
        self.close_func = close_func

        self.CommonArgs = {"app_id": API_ID}
        self.BusinessArgs = {"domain": "iat", "language": "Chinese (Simplified)_China", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    @staticmethod
    def create_url():
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            API_KEY, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

    def closed(self):
        self.is_continue = False

    def statued(self):
        self.is_status = True

    def on_message(self, ws, message):
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                self.error_func(sid, errMsg)
            else:
                data = json.loads(message)["data"]["result"]["ws"]
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                self.success_func(result)
        except Exception as e:
            self.error_func(e, None)

    def on_error(self, ws, error):
        self.error_func(error, None)

    def on_close(self, ws, a, b):
        self.is_continue = False
        self.close_func()

    def on_open(self, ws):
        def run():
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = int(RATE * 0.04)

            audio = pyaudio.PyAudio()

            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)

            status = STATUS_FIRST_FRAME

            while self.is_continue:
                buf = stream.read(CHUNK)
                if not buf:
                    continue
                if self.is_status:
                    status = STATUS_LAST_FRAME
                    self.is_status = False
                if status == STATUS_FIRST_FRAME:
                    d = {"common": self.CommonArgs,
                         "business": self.BusinessArgs,
                         "data": {"status": 0, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    break

            stream.stop_stream()
            stream.close()
            audio.terminate()
            ws.close()

        threading.Thread(target=run).start()

    def start_recognition(self):
        websocket.enableTrace(False)
        wsUrl = self.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    def s(data):
        print(data)


    def e(error, code):
        print(error, code)


    def c():
        print("close")

    recognizer = WhisperRealTimeSpeechRecognizer("ws://192.168.1.164:2025", s, e, c)
    recognizer.start_recognition()

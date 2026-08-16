import json
import os
from socket import gethostname, gethostbyname
from logging import getLogger

from flask import Flask, request, Response, render_template, stream_with_context


class _Configure:
    def __init__(self):
        self.intelligence = None
        self.model = None
        self.api_config = None
        self.languages = None
        self.url = None


def reload_module(intelligence_module):
    Configure.intelligence = intelligence_module


def reload_data(new_model, new_api_config, new_languages, new_url):
    Configure.model = new_model
    Configure.api_config = new_api_config
    Configure.languages = new_languages
    Configure.url = new_url


app = Flask(__name__)
app.static_folder = 'static'


# CORS 设置
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = f'http://{gethostbyname(gethostname())}:52013'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


# API 接口
@app.route("/chat", methods=["POST"])
def chat():
    upload_data = request.get_json()
    question = upload_data.get('question')

    def generate():
        for chunk in Configure.intelligence.text_generator(
                question, Configure.model, False, Configure.api_config, Configure.languages, Configure.url):
            yield json.dumps({'message': {'content': chunk}}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/json')


@app.route("/upload-image", methods=["POST"])
def upload_image():
    upload_data = request.get_json()
    upload_url = upload_data.get('url')

    if os.path.exists(upload_url):
        os.rename(upload_url,
                  f'{os.getcwd()}/engine/static/images/{os.path.basename(upload_url)}')
    new_url = f"./static/images/{os.path.basename(upload_url)}"
    return Response(json.dumps({"url": new_url}), mimetype='application/json')


# Web UI 页面
@app.route('/')
def web():
    return render_template('index.html')


def run():
    log = getLogger('werkzeug')
    log.disabled = True
    host = gethostbyname(gethostname())
    port = 52013
    print(f"Server running at http://{host}:{port}")
    app.run(host=host, port=port)


Configure = _Configure()
if __name__ == "__main__":
    run()
else:
    print("Call", __name__)

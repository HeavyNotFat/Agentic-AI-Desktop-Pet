import time
import os
import socket
import json

import ollama
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# API密钥
allowed_api = "heavynotfat"
client = ollama.Client()
CustomAPI = fastapi.FastAPI()


class Parameters(BaseModel):
    """API参数设定，更改需要对应更改程序的文本输出API部分"""
    # API对比allowed_api的值
    # API在人工智能 -> 本地推理 -> 文本输出API的API-Key字段的value（第二框）填写allowed_api的值
    api: str          # 在 人工智能 -> 本地推理 -> 文本输出API 的API-Key字段的Endpoint（第一框）
    model: str        # 在 人工智能 -> 本地推理 -> 文本输出API 的Model字段的Endpoint（第一框）
    messages: list    # 在 人工智能 -> 本地推理 -> 文本输出API 的Messages字段的Endpoint


@CustomAPI.post("/chat")
def chat(param: Parameters):
    """
    提供聊天功能的API接口。

    使用请填入：http://<您的IP>:<当前年份>/chat
    """
    def event_generator():
        # 对比API密钥，检查传入的API密钥是否与允许的API密钥匹配
        if param.api != allowed_api:
            # 如果API密钥不匹配，生成一个包含错误信息的JSON响应
            yield json.dumps({'message': {'content': 'Invalid API key'}})
        else:
            # 调用ollama客户端的chat方法，进行流式聊天
            response = client.chat(
                stream=True,  # 启用流式响应
                model=param.model,  # 使用传入的模型参数
                messages=param.messages)  # 使用传入的消息参数
            # 遍历聊天响应的每个块
            for chunk in response:
                # 将每个块的内容转换为JSON格式并生成响应
                yield json.dumps({'message': {'content': chunk.message.content}})

    # 返回一个StreamingResponse对象，内容类型为text/event-stream，用于流式传输事件
    return StreamingResponse(event_generator(), media_type="text/event-stream")


os.system("color 0")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(CustomAPI, host=socket.gethostbyname(socket.gethostname()), port=int(time.strftime("%Y")))

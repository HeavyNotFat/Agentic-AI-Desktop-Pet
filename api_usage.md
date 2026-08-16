<div align="center">
    <h1>📚 实时 API 与订阅 API 开发文档</h1>
    <h3>⚠️ 本文档以中文编写，欢迎贡献多语言翻译！ 🌍</h3>
</div>

---

## 📡 实时 API（UDP 协议）

### 核心特性

- 基于 UDP 协议的轻量级通信
- 独立程序专用接口
- 线程安全设计，支持异步调用
- 完全兼容订阅 API 语法规则

---

### 🛠️ 快速接入

```python
import socket
import json
import threading


class RealtimeAPI(threading.Thread):
    def __init__(self, interface, address=('127.0.0.1', 8210)):
        """
        初始化 UDP 客户端线程
        :param interface: dict - 必填，接口配置字典
            - instance: str 实例路径（格式：模块.类）
            - method: str 调用方法名
            - parameter: list 参数列表
        :param address: tuple - 服务端地址，默认本地 8210 端口
        """
        super().__init__()
        self.address = address
        self.interface = interface
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send_request(self, message_dict):
        self.client_socket.sendto(json.dumps(message_dict).encode('utf-8'), self.address)
        response = self.client_socket.recvfrom(1024)[0]
        return response.decode('utf-8') if response != b"None" else None

    def run(self):
        try:
            result = self._send_request(self.interface)
            print(f"[{self.address[0]}:{self.address[1]}] 响应: {result}")
        finally:
            self.client_socket.close()
```

### 📝 接口规范

| 字段          | 类型     | 必填 | 说明                            |
|-------------|--------|----|-------------------------------|
| `instance`  | string | ✅  | 实例路径（例：`subscribe.Character`） |
| `parameter` | list   | ✅  | 参数列表，支持顺序传参或字典传参              |
| `method`    | string | ❌  | 调用方法名（省略时需完整路径）               |

---

### 🎯 使用示例

#### 基础调用

```python
# 获取角色名称
RealtimeAPI({
    "instance": "subscribe.Character",
    "method": "GetName",
    "parameter": []
}).start()
```

#### 高级调用

```python
# 发送系统通知
RealtimeAPI({
    "instance": "setting.customize.widgets",
    "method": "pop_notification",
    "parameter": [
        "操作成功",
        "实时接口调用完成！",
        "success"
    ]
}).start()
```

---

## 📡 订阅 API（程序增强）

### 核心特性

- 面向插件开发的增强接口
- 链式调用语法
- 完善的类型支持

---

### 🧩 基础 API

#### Character 模块

```javascript
interface.subscribe.Character
```

| 方法               | 参数 | 返回值   | 说明          |
|------------------|----|-------|-------------|
| `GetCharacter()` | 无  | `str` | 获取角色模型名称    |
| `GetName()`      | 无  | `str` | 获取用户命名的角色名称 |

**示例：**

```python
# 获取当前角色名称
name = interface.subscribe.Character.GetName()
```

---

#### Window 模块

```javascript
interface.subscribe.Window
```

| 方法                    | 参数 | 返回值     | 说明                             |
|-----------------------|----|---------|--------------------------------|
| `GetWindowPosition()` | 无  | `tuple` | 获取窗口位置信息 (width, height, x, y) |

**数据结构：**

```json
{
  "width": 1920,
  "height": 1080,
  "x": 100,
  "y": 50
}
```

#### Live2D 模块

```javascript
interface.subscribe.Live2D
```

| 方法            | 参数 | 返回值                | 说明          |
|---------------|----|--------------------|-------------|
| `GetLive2D()` | 无  | `live2d.LAppModel` | 获取Live2D的属性 |

**示例：**

```python
# 获取当前角色名称
live2d_attr = interface.subscribe.Live2D.GetLive2D()
```

#### Model 模块

```javascript
interface.subscribe.Model
```

| 方法                | 参数 | 返回值   | 说明         |
|-------------------|----|-------|------------|
| `GetVoiceModel()` | 无  | `str` | 获取角色语音模型名称 |

**示例：**

```python
# 获取当前角色语音模型名称
voice_model = interface.subscribe.Model.GetVoiceModel()
```

---

## 📌 最佳实践

1. 优先使用订阅 API 进行功能扩展
2. 实时 API 推荐用于低延迟场景（如游戏交互）
3. 复杂参数建议使用字典格式提升可读性

---

<div align="center">
    <h3>🚀 期待您的创意实现！</h3>
    <p>遇到问题？欢迎提交 Issue 或 Pull Request</p>
</div>
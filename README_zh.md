<div align="center">
    <h1 style="margin: 0;">人工智能桌面伴侣</h1>
    <br/>
    <b><a href="README.md">English</a></b> | <b><a href="README_zh.md">简体中文</a></b>
    <br/>
</div>

---

## 🌟 项目简介

这是一个由人工智能驱动的桌面宠物应用，支持高度自定义的角色外观、动画和对话功能。它能够通过语音识别与用户互动，并对触摸操作做出实时反应。无论是技术爱好者还是普通用户，都可以轻松上手并享受个性化体验。

> [!NOTE]
> 这不仅仅是一个桌面宠物，更是你的数字助手！

---

## 🚀 核心特点

- **智能对话**  
  基于先进的人工智能技术，实现生动自然的对话交互。

- **完全开源**  
  开源、安全、稳定！代码透明，欢迎贡献。

- **多语言支持**  
  支持中文、英文、日文等多种语言，并可轻松扩展其他语言。

- **高度自定义**  
  自定义角色模型、动画、声音、对话等内容，打造独一无二的桌面伴侣。

- **插件系统**  
  提供丰富的插件和API接口，让你的AI更加智能化、自由化。

---

## 🛠 使用指南

### 添加模型

1. 下载您喜欢的Live2D模型文件。
2. 将文件放置在 `resources/model` 目录下。
3. 重启程序即可加载新模型。

> [!IMPORTANT]
> 如果更换模型失败，请确保已绑定模型数据（`绑定设置 -> 动画绑定`）。

### 绑定设置

#### 扩展工具

扩展工具允许你为AI定义新的函数调用能力。例如：

```python
def process_human_information(name: str, age: int, gender: str):
    """ 处理人类信息的示例函数。 """
    return "Processing Complete!"
```

---

## 📦 支持的外置库

以下是项目依赖的核心库列表：

| 库名               | 版本     |
|------------------|--------|
| pyqt5            | latest |
| pyopengl         | latest |
| pypiwin32        | latest |
| live2d-py        | latest |
| dashscope        | latest |
| requests         | latest |
| pyaudio          | latest |
| numpy            | latest |
| websocket-client | latest |
| mss              | latest |
| pydantic         | latest |
| uvicorn          | latest |
| fastapi          | latest |

---

## 🎯 功能清单

- [x] Live2D 模型支持
- [x] AI 对话引擎
- [x] 多模态AI支持
- [x] 热重载模型
- [x] 插件系统
- [ ] 完全云支持
- [ ] 更多国际化语言

---

## 💡 细节亮点

- **气泡提示**：鼠标悬停时显示详细说明。
- **着色器优化**：支持老设备运行。
- **任务栏兼容**：桌宠不会超出任务栏范围。
- **多语言扩展**：轻松添加新语言支持。

---

## 🙏 致谢

感谢以下开源项目的贡献：

- [Live2D-Py](https://github.com/Arkueid/live2d-py)
- [PyOpenGL](https://github.com/mcfletch/pyopengl.git)
- [Python](https://github.com/python/cpython.git)
- [PyQt5](https://github.com/PyQt5/PyQt.git)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg.git)

---

## 🤝 贡献指南

欢迎提交Issue或Pull Request！让我们一起将这个项目变得更强大！

---

## 📜 许可证

本项目采用GPLv3.0许可证，详情请参阅 [LICENSE](./LICENSE) 文件。

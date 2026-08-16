import os
import json
from typing import Literal
import shutil
import glob

from ..customize import widgets

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QRect
from qfluentwidgets import ProgressRing, BodyLabel, PushButton


class Recovery:
    @staticmethod
    def configure():
        with open("./resources/configure.json", "w", encoding="utf-8") as f:
            json.dump(INITIAL_CONFIGURE, f, indent=3, ensure_ascii=False)
            f.close()

    @staticmethod
    def switch():
        with open("./interface/setting/sub_general/switch.json", "w", encoding="utf-8") as f:
            json.dump(INITIAL_SETTING_SWITCH, f, indent=3, ensure_ascii=False)
            f.close()

    @staticmethod
    def intelligence():
        with open("./interface/setting/sub_general/intelligence.json", "w", encoding="utf-8") as f:
            json.dump(INITIAL_SETTING_INTELLIGENCE, f, indent=3, ensure_ascii=False)
            f.close()

    @staticmethod
    def scripts():
        with open("./engine/static/scripts.js.json", "w", encoding="utf-8") as f:
            f.write(INITIAL_JAVA_SCRIPTS)
            f.close()

    def all(self):
        self.configure()
        self.switch()
        self.intelligence()
        self.scripts()
        # 删除服务器临时图片
        for file in os.listdir("./engine/static/images"):
           os.remove(f"./engine/static/images/{file}")
        # 删除声音
        for file in os.listdir("./resources/voice"):
            if file in EXPECTED_FILE_NAMES:
                continue
            shutil.rmtree(f"./resources/voice/{file}")
        # 删除模型
        for file in os.listdir("./resources/model"):
            if file in EXPECTED_FILE_NAMES:
                continue
            shutil.rmtree(f"./resources/model/{file}")
        # 删除日志
        for file in glob.glob("./logs/history/*.txt"):
            os.remove(file)
        for file in glob.glob("./logs/picture/*.png"):
            os.remove(file)
        for file in glob.glob("./logs/rec/*.txt"):
            os.remove(file)
        # 删除人工智能相关
        for file in os.listdir("./intelligence/prompts"):
            if file in EXPECTED_FILE_NAMES:
                continue
            os.remove(f"./intelligence/prompts/{file}")
        for file in os.listdir("./intelligence/rules"):
            if file in EXPECTED_FILE_NAMES:
                continue
            os.remove(f"./intelligence/rules/{file}")
        # 删除社区
        for file in os.listdir("./resources/community"):
            shutil.rmtree(f"./resources/community/{file}")


class StorageManager(QWidget):
    def __init__(self, languages, configure, runtime):
        super().__init__()
        storage_info = runtime.get_disk_storage_info()
        current_used = int(runtime.get_program_used_storage() * 100)
        current_disk_symbol = str(os.getcwd()).split('\\')[0]
        total_space_in_disk = storage_info[current_disk_symbol][0] * 100
        used_rate_total = round(current_used / (storage_info["*"][0] * 100), 2) * 100
        used_rate_current_disk = round(current_used / total_space_in_disk, 2) * 100

        self.languages = languages
        self.configure = configure
        self.setObjectName("StorageManager")

        BodyLabel(self.languages[219].format(disk=current_disk_symbol),
                  self).setGeometry(QRect(0, 250, 650, 30))
        self.ring_current_disk = ProgressRing(self)
        self.ring_current_disk.setRange(0, total_space_in_disk)
        self.ring_current_disk.setValue(current_used)
        self.ring_current_disk.setTextVisible(True)
        self.ring_current_disk.setFixedSize(200, 200)
        self.ring_current_disk.setStrokeWidth(4)
        self.ring_current_disk.setGeometry(QRect(10, 42, 200, 200))
        self.ring_current_disk.setFormat(f"{used_rate_current_disk} %" if used_rate_current_disk > 0.1 else "<= 0.1%")

        BodyLabel(self.languages[220], self).setGeometry(QRect(440, 250, 650, 30))
        self.ring_total_disk = ProgressRing(self)
        self.ring_total_disk.setRange(0, storage_info["*"][0] * 100)
        self.ring_total_disk.setValue(current_used)
        self.ring_total_disk.setTextVisible(True)
        self.ring_total_disk.setFixedSize(200, 200)
        self.ring_total_disk.setStrokeWidth(4)
        self.ring_total_disk.setGeometry(QRect(440, 42, 200, 200))
        self.ring_total_disk.setFormat(f"{used_rate_total} %" if used_rate_total > 0.1 else "<= 0.1%")

        self.click_recover_all = PushButton(self.languages[221], self)
        self.click_recover_all.clicked.connect(lambda: self.recovery(self.languages[221], "all"))
        self.click_recover_all.setGeometry(QRect(10, 300, 150, 30))

        self.click_recover_configure = PushButton(self.languages[222], self)
        self.click_recover_configure.clicked.connect(lambda: self.recovery(self.languages[222], "configure"))
        self.click_recover_configure.setGeometry(QRect(10, 350, 150, 30))

        self.click_recover_switch = PushButton(self.languages[223], self)
        self.click_recover_switch.clicked.connect(lambda: self.recovery(self.languages[223], "switch"))
        self.click_recover_switch.setGeometry(QRect(160, 350, 150, 30))

        self.click_recover_intelligence = PushButton(self.languages[224], self)
        self.click_recover_intelligence.clicked.connect(lambda: self.recovery(self.languages[224], "intelligence"))
        self.click_recover_intelligence.setGeometry(QRect(310, 350, 150, 30))

        self.click_recover_scripts = PushButton(self.languages[225], self)
        self.click_recover_scripts.clicked.connect(lambda: self.recovery(self.languages[225], "scripts"))
        self.click_recover_scripts.setGeometry(QRect(460, 350, 150, 30))

    def recovery(self, description, type_: Literal['all', 'configure', 'switch', 'intelligence', 'scripts'] = "all"):
        if not widgets.pop_message(self, self.languages[226], f"{self.languages[232]}({description})"):
            widgets.pop_notification(self.languages[78], self.languages[229], "error")
            return
        if type_ == "all" and not widgets.pop_message(
                self, f"⚠️{self.languages[228]}⚠️",
                f"{'⚠️' * 25}\n{self.languages[231]}\n{'⚠️' * 25}"):
            widgets.pop_notification(self.languages[78], self.languages[229], "error")
            return
        if hasattr(Recovery, type_):
            getattr(Recovery, type_)()
            widgets.pop_success(self, self.languages[227], f"{description}{self.languages[227]}")
        else:
            widgets.pop_error(self, self.languages[78], f"{description}{self.languages[230]}")


INITIAL_CONFIGURE = {
   "name": "巧克力",
   "voice_model": "巧克力",
   "default": "Chocola",
   "watermark": "Keep@NoneParameter;0.0",
   "adult_level": 0,
   "settings": {
      "language": "",
      "python": "",
      "angle": 0.0,
      "size": 1.0,
      "transparency": 1.0,
      "compatibility": False,
      "safety": "shut",
      "intelligence": "qwen-max-latest",
      "translate": "spider.bing",
      "trans_lang": "ja",
      "physics": {
         "total": True,
         "bounce": True,
         "dumping": True
      },
      "live2d": {
         "enable": {
            "AutoBlink": True,
            "AutoBreath": True,
            "AutoDrag": True
         }
      },
      "enable": {
         "visualization": False,
         "tts": False,
         "media": True,
         "online": False,
         "trans": True,
         "rec": False,
         "locktsk": True,
         "realtimeAPI": False
      },
      "cloud": {
         "aliyun": "",
         "xunfei": {
            "id": "",
            "key": "",
            "secret": ""
         }
      },
      "local": {
         "text": "http://{ip}:{year}/chat",
         "media": "https://{ip}:{year}/media",
         "gsv": "http://{ip}:{year} + 1",
         "rec": {
            "tool": "whisper",
            "url": "ws://{ip}:{year} + 3"
         }
      },
      "tts": {
         "way": "cloud",
         "top_k": 25,
         "top_p": 0.8,
         "temperature": 0.8,
         "speed": 1.0,
         "batch_size": 3,
         "batch_threshold": 0.75,
         "parallel": True
      },
      "text": {
         "way": "cloud",
         "temperature": 0.8,
         "top_p": 0.8,
         "top_k": 20
      },
      "rec": {
         "way": "cloud",
         "silence_threshold": None,
         "silence_duration": 0.6
      },
      "understand": {
         "way": "cloud",
         "min": 3600,
         "max": 7200
      },
      "setting": {
         "silence_threshold": None
      }
   },
   "model": {
      "Chocola": {
         "adult": {
            "AdultContent": False,
            "AdultLevelMinimum": 1,
            "AdultLevelMaximum": 5,
            "AdultDescribe": {
               "1": "娇喘 Gasp",
               "2": "裸露 Nudity",
               "3": "行为 Sex",
               "4": "互动 Interact",
               "5": "模拟 Simulate"
            },
            "action": {
               "ActionSex": []
            },
            "voice": {
               "VoiceGasp": []
            }
         },
         "action": {
            "ActionTouchHead": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            },
            "ActionTouchLeg": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            },
            "ActionClickCap": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            },
            "ActionClickChest": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            },
            "ActionTouchCustom": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            },
            "ActionClickCustom": {
               "position": [
                  -1,
                  -1,
                  -1,
                  -1
               ],
               "motion": "None:motions/None.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            }
         },
         "voice": {
            "angry": [],
            "coquetry": [],
            "happy": [],
            "sad": [],
            "stable": [],
            "welcome": []
         },
         "special_action": {
            "ActionLogin": {
               "motion": "None:motions/None`.json:0",
               "expression": "",
               "play": "",
               "play_type": ""
            }
         }
      }
   },
   "language_mapping": {
      "Chinese (Simplified)_China": "zh-Hans",
      "English_United States": "en",
      "Japanese_Japan": "ja",
      "Korean_Korea": "ko"
   },
   "record": {
      "position": [
         -1,
         -1,
         -1,
         -1
      ],
      "enable_position": False
   },
   "api_source": "https://api.nekocode.top/api/adp"
}

SWITCHES = {
   "Advanced": {
      "penetration": "shut",
      "safety": "shut",
      "python": ""
   },
   "QFluentWidgets": {
      "ThemeColor": "#ff009faa",
      "ThemeMode": "Light"
   }
}

INITIAL_SETTING_INTELLIGENCE = {
    "Inference": {
        "media": "cloud",
        "recognition": "cloud",
        "text_output": "cloud",
        "voice": "cloud"
    },
    "QFluentWidgets": {
        "ThemeColor": "#ff009faa",
        "ThemeMode": "Light"
    }
}

INITIAL_JAVA_SCRIPTS = r"""document.getElementById('send-button').addEventListener('click', async function() {
    // 获取输入框中的消息（即问题）
    var question = document.getElementById('message-input').value;

    if (!question) {
        alert("请输入您的问题！");
        return;
    }
    document.getElementById('message-input').value = "";
    var requestBody = {
        question: question
    };
    // 添加用户消息到聊天窗口
    addMessage(question, 'user');
    try {
        const response = await fetch('{PYTHON_UPLOAD_URL_ADDRESS}/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        if (!response.body) {
            throw new Error('ReadableStream not available in this environment');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let partialMessage = '';

        // 创建一个新的AI消息元素
        let aiMessageElement = document.createElement('div');
        aiMessageElement.classList.add('chat-message');
        let aiTextElement = document.createElement('div');
        aiTextElement.classList.add('ai-message');
        aiMessageElement.appendChild(aiTextElement);
        document.getElementById('chat-window').appendChild(aiMessageElement);
        document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
        document.getElementById('result').innerText = '思考中';

        // 正则表达式匹配Markdown格式的图片
        const imgRegex = /!\[.*?\]\((.*?)\)/g;

        let hasProcessed = [];

        while (True) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: True });
            partialMessage += chunk;

            const messages = partialMessage.split('\n');
            partialMessage = messages.pop();

            for (const message of messages) {
                if (message.trim()) {  // 忽略空字符串
                    try {
                        const parsedMessage = JSON.parse(message);

                        console.log(parsedMessage)

                        // 截取message.content并更新UI
                        if (parsedMessage && parsedMessage.message.content) {
                            // 移除重复内容
                            let content = parsedMessage.message.content;
                            if (aiTextElement.textContent) {
                                content = content.replace(aiTextElement.textContent, '');
                            }
                            document.getElementById('result').innerText = '输出中……';

                            // 提取图片并渲染
                            let imgMatch;
                            while ((imgMatch = imgRegex.exec(content)) !== null) {
                                const imgUrl = imgMatch[1];
                                // 判断是否已经刷新过了
                                if ((hasProcessed.find(value => value === imgUrl)) != undefined) {
                                    break;
                                }
                                hasProcessed.push(imgUrl);
                                // 发送图片URL到后端，获取新的URL
                                const uploadResponse = await fetch('{PYTHON_UPLOAD_URL_ADDRESS}/upload-image', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ url: imgUrl })
                                });
                                if (uploadResponse.ok) {
                                    const uploadResult = await uploadResponse.json();
                                    const newImgUrl = uploadResult.url;
                                    const imgElement = document.createElement('img');
                                    imgElement.src = newImgUrl;
                                    imgElement.style.maxWidth = '50%'; // 缩小图片到原来的一半
                                    imgElement.style.height = 'auto'; // 保持图片比例
                                    aiMessageElement.appendChild(imgElement); // 先添加图片
                                } else {
                                    console.error('Failed to upload image:', uploadResponse.statusText);
                                }
                            }

                            // 渲染剩余文本
                            const textContent = content.replace(imgRegex, '').trim();
                            if (textContent) {
                                aiTextElement.innerHTML = marked.parse(textContent);
                            }

                            document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
                        }
                    } catch (e) {
                        console.error('Failed to parse message:', e);
                    }
                }
            }
        }
        document.getElementById('result').innerText = '';
    } catch (error) {
        console.error('Error:', error);
        addMessage('Failed to send message', 'ai');
    }
});

document.getElementById('message-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // 阻止默认的换行行为
        document.getElementById('send-button').click(); // 触发发送按钮的点击事件
    }
});

function addMessage(text, sender) {
    var chatWindow = document.getElementById('chat-window');
    var messageElement = document.createElement('div');
    messageElement.classList.add('chat-message');
    var textElement = document.createElement('div');
    textElement.textContent = text;
    textElement.classList.add(sender + '-message');
    messageElement.appendChild(textElement);
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}"""
INITIAL_SETTING_SWITCH = {
   "Advanced": {
      "penetration": "shut",
      "safety": "shut",
      "python": ""
   },
   "QFluentWidgets": {
      "ThemeColor": "#ff009faa",
      "ThemeMode": "Light"
   }
}
EXPECTED_FILE_NAMES = ("kasumi2", "Chocola", "kasumi2.json", "Chocola.json")

Recovery = Recovery()

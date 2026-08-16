"""
@Author:  HeavyNotFat
@Idea: 由服务端接受请求后交给interface.subscribe进行解析
@Usage:
   客户端必须为UDP协议！
   客户端必须为UDP协议！
   客户端必须为UDP协议！

   客户端接受最少2个参数，采用JSON
      instance        $ string. 实例路径，以点分割
      parameter       $ dict | list. 传参，dict为点对点传参，list为顺序传参
   客户端接受最多3个参数，采用JSON
      instance        $ string. 继承实例路径，以点分割
      method          $ string. 调用实例方法
      parameter       $ dict | list. 传参，dict为点对点传参，list为顺序传参
   要求：
      1、 如果不穿入method，instance就传入全部的路径
      2、 如果传入method，instance就只传入继承路径
      3、 parameter如果为字典(dict)，字典的键为传入的参数名，对应的值为传入的参数值
      4、 parameter如果为列表(list)，就以传入的顺序传参
   示例：
      {
        "instance": "subscribe.Character.GetName",
        "parameter": []
      }
      Character.GetName是实例路径
      和
      {
        "instance": "subscribe.Character",
        "method": "GetName"
        "parameter": []
      }
      是等效的
      Character是继承路径，GetName是调用的实例方法

      这个等于
      interface.subscribe.Character.GetName()
"""
import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal


class UDPServer(QThread):
    calling = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str, tuple)
    server_stopped = pyqtSignal()
    server_started = pyqtSignal()

    def __init__(self, host='0.0.0.0', port=8210):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def run(self):
        """启动UDP服务器并开始接收数据"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            self.running = True
            self.server_started.emit()
            print(f"UDP Server started at {self.host}:{self.port}")

            while self.running:
                data, address = self.server_socket.recvfrom(65535)
                interface_data = json.loads(data.decode('utf-8'))
                print(f"[{address}]: {interface_data}")

                # 处理请求逻辑
                try:
                    if "method" in interface_data:
                        calling = f"{interface_data['instance']}.{interface_data['method']}"
                    else:
                        calling = interface_data['instance']

                    response = self.calling.emit(calling, interface_data.get('parameter', []))
                    self.handle_message(response, address)
                except Exception as e:
                    print(f"Error occurred: {e}")
                    self.error_occurred.emit(f"Error: {e}", address)

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def handle_message(self, callback, address):
        """处理客户端消息并发送响应"""
        self.server_socket.sendto(str(callback).encode('utf-8'), address)

    def stop(self):
        """停止服务端"""
        if self.running is False:
            return
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.server_stopped.emit()
        print("UDP Server stopped.")

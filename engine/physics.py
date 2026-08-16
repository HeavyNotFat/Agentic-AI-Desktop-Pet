"""
物理演算！
"""
class BasePhysics:
    def __init__(self):
        # 初始速度
        self.velocity_y = 0.0
        self.velocity_x = 0.0
        # 加速度
        self.acceleration = 0.43
        # 弹性系数
        self.restitution = 0.73

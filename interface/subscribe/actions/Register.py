class Register:
    def __init__(self, config):
        self.config = config

    # 注册
    def SetDragEnterAction(self, func: callable):
        """
        注册拖拽进入事件
        :param func: callable  -->   可调用函数
        :callback:
            event             --> QMimeData  ->  原始Mime
            analyzed_action   --> list[tuple[str, str]] 程序已经处理的Mime
        """
        self.config.register("drag_enter_action", func)

    def SetDragLeaveAction(self, func: callable):
        """
        注册拖拽离开事件
        :param func: callable  -->   可调用函数
        :callback:
            event             --> QMimeData  ->  原始Mime
            analyzed_action   --> list[tuple[str, str]] 程序已经处理的Mime
        """
        self.config.register("drag_leave_action", func)

    def SetDragMoveAction(self, func: callable):
        """
        注册拖拽移动事件
        :param func: callable  -->   可调用函数
        :callback:
            event             --> QMimeData  ->  原始Mime
            analyzed_action   --> list[tuple[str, str]] 程序已经处理的Mime
        """
        self.config.register("drag_move_action", func)

    def SetDropAction(self, func: callable):
        """
        注册拖拽释放事件
        :param func: callable  -->   可调用函数
        :callback:
            event             --> QMimeData  ->  原始Mime
            analyzed_action   --> list[tuple[str, str]] 程序已经处理的Mime
        """
        self.config.register("drag_drop_action", func)

    def SetClickAction(self, func: callable):
        """
        注册点击宠物的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("click_action", func)

    def SetMouseEnterAction(self, func: callable):
        """
        注册鼠标进入宠物的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("mouse_enter_action", func)

    def SetMouseLeaveAction(self, func: callable):
        """
        注册鼠标离开宠物的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("mouse_leave_action", func)

    def SetMouseMoveAction(self, func: callable):
        """
        注册鼠标在宠物内移动的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("mouse_move_action", func)

    def SetMouseDragAction(self, func: callable):
        """
        注册宠物被拖拽的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("mouse_drag_action", func)

    def SetMouseReleaseAction(self, func: callable):
        """
        注册鼠标释放宠物的事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("mouse_release_action", func)

    def SetAIOutput(self, func: callable):
        """
        注册AI输出事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("ai_output", func)

    def SetRecognitionOutput(self, func: callable):
        """
        注册识别输出事件
        :param func: callable  -->   可调用函数
        """
        self.config.register("recognition_output", func)

    # 注销
    def UnsetDragEnterAction(self):
        self.config.unregister("drag_enter_action")

    def UnsetDragLeaveAction(self):
        self.config.unregister("drag_leave_action")

    def UnsetDragMoveAction(self):
        self.config.unregister("drag_move_action")

    def UnsetDragDropAction(self):
        self.config.unregister("drag_drop_action")

    def UnsetClickAction(self):
        self.config.unregister("click_action")

    def UnsetMouseEnterAction(self):
        self.config.unregister("mouse_enter_action")

    def UnsetMouseLeaveAction(self):
        self.config.unregister("mouse_leave_action")

    def UnsetMouseMoveAction(self):
        self.config.unregister("mouse_move_action")

    def UnsetMouseDragAction(self):
        self.config.unregister("mouse_drag_action")

    def UnsetAIOutput(self):
        self.config.unregister("ai_output")

    def UnsetRecognitionOutput(self):
        self.config.unregister("recognition_output")

    def UnsetALL(self):
        self.UnsetDragEnterAction()
        self.UnsetDragLeaveAction()
        self.UnsetDragMoveAction()
        self.UnsetDragDropAction()
        self.UnsetClickAction()
        self.UnsetMouseEnterAction()
        self.UnsetMouseLeaveAction()
        self.UnsetMouseMoveAction()
        self.UnsetMouseDragAction()
        self.UnsetAIOutput()
        self.UnsetRecognitionOutput()

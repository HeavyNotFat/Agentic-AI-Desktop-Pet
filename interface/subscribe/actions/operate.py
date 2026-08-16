class Operate:
    def __init__(self, config):
        self.config = config

    def GetDragEnterAction(self) -> list:
        return self.config['drag_enter_action']

    def GetDragLeaveAction(self) -> list:
        return self.config['drag_leave_action']

    def GetDragMoveAction(self) -> list:
        return self.config['drag_move_action']

    def GetDropAction(self) -> list:
        return self.config['drag_drop_action']

    def GetClckAction(self) -> list:
        return self.config['click_action']

    def GetMouseEnterAction(self) -> list:
        return self.config['mouse_enter_action']

    def GetMouseLeaveAction(self) -> list:
        return self.config['mouse_leave_action']

    def GetMouseMoveAction(self) -> list:
        return self.config['mouse_move_action']

    def GetMouseDragAction(self) -> list:
        return self.config['mouse_drag_action']

    def GetMouseReleaseAction(self) -> list:
        return self.config['mouse_release_action']

    def GetAIOutput(self) -> list:
        return self.config['ai_output']

    def GetRecognitionOutput(self) -> list:
        return self.config['recognition_output']

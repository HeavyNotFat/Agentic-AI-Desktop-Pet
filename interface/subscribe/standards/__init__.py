"""
@Author: HeavyNotFat
@Explanation: Constants and global variables used to load something special
@Namespace: <suffix> CONTENT
"""


class _StoppingException:
    pass


# Sub Interface
SUB_PROGRAM_SELF = 0
SUB_GENERAL = 1
SUB_INTELLIGENCE = 2
SUB_BINDING = 3
SUB_DEVELOPER = 4
SUB_ABOUT = 5

# Program analysis mime data for mouse dragging
MIME_DRAG_FILE = "drag_file"
MIME_DRAG_FOLDER = "drag_folder"
MIME_DRAG_PURE_TEXT = "drag_pure_text"

# STOP function executing
STOP_EXECUTING_NEXT = _StoppingException()

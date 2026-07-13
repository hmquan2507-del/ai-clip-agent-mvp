from enum import Enum


class ReviewAction(str, Enum):
    """
    Defines the set of actions that can be performed on a Review Workspace.
    """
    OPEN = "OPEN"
    SAVE = "SAVE"
    UNDO = "UNDO"
    REDO = "REDO"
    APPROVE_AI = "APPROVE_AI"
    REJECT_AI = "REJECT_AI"
    RENDER_PREVIEW = "RENDER_PREVIEW"
    EXPORT = "EXPORT"
    DELETE = "DELETE"

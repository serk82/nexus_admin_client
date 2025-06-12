from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QWidget


def track_user_activity(cls):
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.installEventFilter(self)
        for child in self.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.KeyPress):
            if hasattr(self, "auth_manager"):
                self.auth_manager.is_token_expired(self)
                self.auth_manager.record_activity()
        return False

    cls.__init__ = new_init
    cls.eventFilter = eventFilter
    return cls

from controllers import AuthManager
from lib.exceptions import *
from PyQt6.QtWidgets import QDialog
from views.forms_py import Ui_frm_notification_settings


class frm_notification_settings(QDialog):

    def __init__(self, form, auth_manager: AuthManager, user_id: int):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.ui = Ui_frm_notification_settings()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)

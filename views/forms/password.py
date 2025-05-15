from controllers import AuthManager, UsersController
from views.forms_py import Ui_frm_password
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox


class frm_password(QDialog):

    password = pyqtSignal(str)

    def __init__(self, form, auth_manager: AuthManager):
        super().__init__(form)
        self.ui = Ui_frm_password()
        self.ui.setupUi(self)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.users_controller = UsersController()

        # Events
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)

    def save(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_password.text():
            QMessageBox.information(self, " ", "La contraseña no puede estar vacía")
            return
        if not self.ui.txt_repeat_password.text():
            QMessageBox.information(
                self, " ", "La contraseña repetida no puede estar vacía"
            )
            return
        if self.ui.txt_password.text() != self.ui.txt_repeat_password.text():
            QMessageBox.information(self, " ", "Las contraseñas no coinciden")
            return
        self.password.emit(self.ui.txt_password.text())
        self.close()

import os
from controllers import AuthManager
from views.forms_py import Ui_frm_login
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
)


class frm_login(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_frm_login()
        self.ui.setupUi(self)

        # Configuración de la ventana principal
        self.setWindowTitle("Nexus Admin")

        self.ui.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Crear el layout para los botones de "Entrar" y "Salir"
        btn_layout = QHBoxLayout()
        btn_layout.setObjectName("btn_layout")

        # Events
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.txt_password.returnPressed.connect(self.login)
        self.ui.btn_exit.clicked.connect(self.close)

        # Crear el QLabel para el logo
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        logo_path = os.path.join(BASE_DIR, "img", "logo.png")
        self.logo_pixmap = QPixmap(logo_path)
        self.ui.lbl_logo.setPixmap(
            self.logo_pixmap.scaled(
                100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        # Set version at label
        from views.forms import frm_update

        self.ui.lbl_version.setText(
            f"versión {frm_update.get_local_version(self)['VERSION']}"
        )

        # Tab Order
        self.setTabOrder(self.ui.txt_username, self.ui.txt_password)
        self.setTabOrder(self.ui.txt_password, self.ui.btn_login)
        self.ui.txt_username.setFocus()

    def login(self):
        from views.forms import frm_options, frm_notifications

        username = self.ui.txt_username.text()
        password = self.ui.txt_password.text()

        auth_manager = AuthManager()
        if auth_manager.login(username, password):
            self.form = frm_notifications(auth_manager)
            self.form.exec()
            self.form = frm_options(auth_manager)
            self.form.show()
            self.close()
        else:
            QMessageBox.information(self, " ", "Usuario o contraseña incorrecto!")

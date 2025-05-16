import os, sys
from controllers import AuthManager
from views.forms_py import Ui_frm_login
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from __version__ import VERSION


class frm_login(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_frm_login()
        self.ui.setupUi(self)

        # Configuración de la ventana principal
        self.setWindowTitle("Nexus Admin")

        # Crear el layout principal
        main_layout = QVBoxLayout()

        # Crear el formulario (campos de texto)
        form_layout = QVBoxLayout()

        self.ui.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Crear el layout para los botones de "Entrar" y "Salir"
        btn_layout = QHBoxLayout()
        btn_layout.setObjectName("btn_layout")

        self.ui.btn_login.clicked.connect(self.login)

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
        self.ui.lbl_version.setText(f"v{VERSION}")


    def login(self):
        from views.forms.options import frm_options

        username = self.ui.txt_username.text()
        password = self.ui.txt_password.text()

        auth_manager = AuthManager()
        if auth_manager.login(username, password):
            self.form = frm_options(auth_manager)
            self.form.show()
            self.close()
        else:
            QMessageBox.information(self, " ", "Usuario o contraseña incorrecto!")

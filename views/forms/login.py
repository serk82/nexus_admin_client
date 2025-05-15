from controllers import AuthManager
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)


class frm_login(QWidget):
    def __init__(self):
        super().__init__()
        # Configuración de la ventana principal
        self.setWindowTitle("Nexus Admin")
        self.setGeometry(100, 100, 280, 250)

        # Crear el layout principal
        main_layout = QVBoxLayout()

        # Crear el formulario (campos de texto)
        form_layout = QVBoxLayout()

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Usuario")

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Contraseña")

        # Añadir los campos de texto al formulario
        form_layout.addWidget(self.txt_username)
        form_layout.addWidget(self.txt_password)

        # Crear el layout para los botones de "Entrar" y "Salir"
        btn_layout = QHBoxLayout()
        btn_layout.setObjectName("btn_layout")

        self.btn_login = QPushButton("Entrar")
        self.btn_login.clicked.connect(self.login)

        self.btn_exit = QPushButton("Salir")
        self.btn_exit.clicked.connect(self.close)

        # Añadir los botones al layout horizontal
        btn_layout.addWidget(self.btn_exit)
        btn_layout.addWidget(self.btn_login)

        # Crear el QLabel para el logo
        self.lbl_logo = QLabel()
        self.logo_pixmap = QPixmap("img/logo.png")
        self.lbl_logo.setPixmap(
            self.logo_pixmap.scaled(
                100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        # # Añadir el logo al layout principal (centrado)
        main_layout.addWidget(self.lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        # Añadir el formulario y los botones al layout principal
        main_layout.addLayout(form_layout)
        main_layout.addItem(spacer)
        main_layout.addLayout(btn_layout)

        # Establecer el layout de la ventana
        self.setLayout(main_layout)

        self.setFixedSize(self.size())

        self.txt_username.setText("admin")
        self.txt_password.setText("1")

    def login(self):
        from views.forms.options import frm_options

        username = self.txt_username.text()
        password = self.txt_password.text()
        
        auth_manager = AuthManager()
        if auth_manager.login(username, password):
            self.form = frm_options(auth_manager)
            self.form.show()
            self.close()
        else:
            QMessageBox.information(self, " ", "Usuario o contraseña incorrecto!")

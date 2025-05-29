import sys
from .main import frm_main
from controllers import CompaniesController, UsersController
from controllers import AuthManager
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QListWidgetItem,
)
from views.forms.configuration import frm_configuration


class frm_options(QDialog):

    def __init__(self, auth_manager: AuthManager):
        super().__init__()
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        self.companies_controller = CompaniesController()
        self.users_controller = UsersController()
        self.user_companies = []

        # Configurar la ventana para que no tenga bordes y sea transparente
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Sin bordes
        self.setGeometry(400, 200, 400, 300)

        # Crear lista de opciones
        self.listWidget = QListWidget(self)
        self.listWidget.setFont(QFont("Ubuntu", 11))  # Fuente elegante

        # self.listWidget.setGridSize(QSize(self.listWidget.width(), 25))

        if self.auth_manager.has_permission("CT"):
            # Agregar opción de configuración
            item = QListWidgetItem("CONFIGURACIÓN")
            item.setData(Qt.ItemDataRole.UserRole, 0)
            self.listWidget.addItem(item)
            self.user_companies = self.companies_controller.get_companies(
                self.auth_manager.token
            )
        else:
            companies_id = self.users_controller.get_companies_from_user(
                self.auth_manager.token, self.auth_manager.user_id
            )
            for company_id in companies_id:
                self.user_companies.append(
                    self.companies_controller.get_company(
                        self.auth_manager.token, company_id
                    )
                )
        if self.user_companies:
            for company in self.user_companies:
                item = QListWidgetItem(company.get("name"))
                item.setData(Qt.ItemDataRole.UserRole, company.get("id"))
                self.listWidget.addItem(item)
        else:
            QMessageBox.information(self, " ", "No tienes acceso a ninguna empresa. Ponte en contacto con el administrador.")
            sys.exit(0)

        self.listWidget.setCurrentRow(0)

        # Crear los botones de Aceptar y Salir
        self.accept_button = QPushButton("Entrar", self)
        self.accept_button.clicked.connect(self.accept)  # Conectar al método accept
        self.exit_button = QPushButton("Salir", self)
        self.exit_button.clicked.connect(self.reject)  # Conectar al método reject
        self.listWidget.doubleClicked.connect(self.accept)

        # Colocar los botones en un layout horizontal
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.exit_button)
        button_layout.addWidget(self.accept_button)

        # Diseño de la ventana
        layout = QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addLayout(button_layout)  # Añadir el layout de botones
        self.setLayout(layout)

    def accept(self):
        selected = self.listWidget.selectedIndexes()
        if selected:
            option_selected = self.listWidget.selectedIndexes()[0].data(
                Qt.ItemDataRole.UserRole
            )
            match option_selected:
                case 0:
                    self.configuration = frm_configuration(self.auth_manager)
                    self.configuration.show()
                    self.close()
                case _:
                    self.form = frm_main(self.auth_manager, option_selected)
                    self.form.show()
                    self.close()
        else:
            QMessageBox.warning(self, " ", "No se ha elegido ninguna opción.")

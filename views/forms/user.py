from controllers import (
    AuthManager,
    RolesController,
    UsersController,
    CompaniesController,
)
from lib.exceptions import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QFrame,
    QHBoxLayout,
)
from views.forms_py import Ui_frm_user


class frm_user(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, id):
        super().__init__(form)
        self.ui = Ui_frm_user()
        self.ui.setupUi(self)

        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.users_controller = UsersController()
        self.roles_controller = RolesController()
        self.companies_controller = CompaniesController()

        # Attributes
        self.frm_users = form
        self.edit = edit
        self.id = id
        self.password = None

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_reset_password.clicked.connect(self.generate_password)

        if id == "1":
            self.ui.groupBox.setEnabled(False)
            self.ui.twd_companies.setVisible(False)
        else:
            # Config table widget of companies
            self.companies = self.companies_controller.get_companies(
                self.auth_manager.token
            )
            self.ui.twd_companies.setRowCount(len(self.companies))
            self.ui.twd_companies.setColumnCount(3)
            self.ui.twd_companies.setHorizontalHeaderLabels(["ID", "Empresa", "Acceso"])
            self.ui.twd_companies.horizontalHeader().setStyleSheet(
                "QHeaderView::section { font-weight: normal; }"
            )
            self.ui.twd_companies.verticalHeader().setVisible(False)
            self.ui.twd_companies.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch
            )
            self.ui.twd_companies.setColumnHidden(0, True)
            self.ui.twd_companies.setColumnWidth(2, 100)
            for row, company in enumerate(self.companies):
                self.ui.twd_companies.setItem(
                    row, 0, QTableWidgetItem(str(company.get("id")))
                )
                self.ui.twd_companies.setItem(
                    row, 1, QTableWidgetItem(company.get("name"))
                )
                checkbox = QCheckBox()
                checkbox.setChecked(False)
                qframe = QFrame()
                layout = QHBoxLayout()
                layout.addWidget(checkbox)
                layout.setAlignment(checkbox, Qt.AlignmentFlag.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                qframe.setLayout(layout)
                self.ui.twd_companies.setCellWidget(row, 2, qframe)

        # Get all roles
        roles = self.roles_controller.get_roles(self.auth_manager.token)

        # Set the roles in the combobox
        num_elements = self.ui.cmb_role.count()
        for role in range(num_elements):
            if role == self.roles_controller.get_role(user.role_id).name:
                self.ui.cmb_role.setCurrentText(role)
                break

        for index, role in enumerate(roles):
            self.ui.cmb_role.addItem(role["name"])
            self.ui.cmb_role.setItemData(index, role["id"])

        if edit:
            self.setWindowTitle("Editar usuario")
            self.ui.btn_save.setText("Guardar")
            user = self.users_controller.get_user_by_id(self.auth_manager.token, id)
            self.ui.txt_username.setText(user["username"])
            self.ui.txt_name.setText(user["name"])
            self.ui.txt_lastname.setText(user["lastname"])
            self.ui.txt_email.setText(user["email"])

            # Get name's role
            role_name = self.roles_controller.get_role(
                self.auth_manager.token, user.get("role_id")
            ).get("name")
            # Set the role in the combobox
            self.ui.cmb_role.setCurrentText(role_name)
            # Set companies from user
            self.user_companies = self.users_controller.get_companies_from_user(
                self.auth_manager.token, self.id
            )
            for row_twd in range(self.ui.twd_companies.rowCount()):
                qframe = self.ui.twd_companies.cellWidget(row_twd, 2)
                column_company = self.ui.twd_companies.item(row_twd, 0)
                for row_user_company in self.user_companies:
                    if int(column_company.text()) == row_user_company.get("id"):
                        checkbox = qframe.findChild(QCheckBox)
                        checkbox.setChecked(True)

        else:
            self.setWindowTitle("Añadir usuario")
            self.ui.btn_save.setText("Añadir")
            self.ui.btn_reset_password.setText("Generar contraseña")

    def collect_user_companies(self):
        companies = []
        for row in range(self.ui.twd_companies.rowCount()):
            qframe = self.ui.twd_companies.cellWidget(row, 2)
            column_company = self.ui.twd_companies.item(row, 0)
            if column_company:
                company_id = column_company.text()
            if qframe:
                checkbox = qframe.findChild(QCheckBox)
                if checkbox:
                    if checkbox.isChecked():
                        companies.append(int(company_id))
        return companies

    def collect_user_data(self):
        return {
            "id": self.id,
            "username": self.ui.txt_username.text(),
            "password": self.password,
            "name": self.ui.txt_name.text(),
            "lastname": self.ui.txt_lastname.text(),
            "email": self.ui.txt_email.text(),
            "role_id": self.ui.cmb_role.currentData(),
        }

    def generate_password(self):
        from views.forms import frm_password

        form = frm_password(self, self.auth_manager)
        form.password.connect(self.set_password)
        form.exec()

    def save(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_username.text():
            QMessageBox.information(self, " ", "El usuario no puede estar vacío")
            return
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                user = self.collect_user_data()
                companies = self.collect_user_companies()
                response = self.users_controller.update_user(
                    self.auth_manager.token, user, companies
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    QMessageBox.information(
                        self,
                        " ",
                        "Cambios guardados correctamente.",
                    )
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido guardar los cambios: {response['error']}",
                    )
        else:
            if not self.password:
                QMessageBox.information(self, " ", "Debes generar una contraseña")
                return
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres añadir el usuario?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                user = self.collect_user_data()
                companies = self.collect_user_companies()
                response = self.users_controller.add_user(
                    self.auth_manager.token, user, companies
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    QMessageBox.information(
                        self,
                        " ",
                        "Usuario creado correctamente.",
                    )
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido añadir el usuario. {': ' + response['error'] if response else ''}",
                    )

    def set_password(self, password):
        self.password = password

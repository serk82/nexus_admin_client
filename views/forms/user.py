from controllers import AuthManager, RolesController, UsersController
from lib.exceptions import *
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
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

        # Get all roles
        roles = self.roles_controller.get_roles(self.auth_manager.token)
        
        # Set the roles in the combobox
        num_elements = self.ui.cmb_role.count()
        for role in range(num_elements):
            if role == self.roles_controller.get_role(user.role_id).name:
                self.ui.cmb_role.setCurrentText(role)
                break

        for index, role in enumerate(roles):
            self.ui.cmb_role.addItem(role['name'])
            self.ui.cmb_role.setItemData(index, role['id'])

        if edit:
            self.setWindowTitle("Editar usuario")
            self.ui.btn_save.setText("Guardar")
            user = self.users_controller.get_user_by_id(self.auth_manager.token, id)
            self.ui.txt_username.setText(user['username'])
            self.ui.txt_name.setText(user['name'])
            self.ui.txt_lastname.setText(user['lastname'])
            self.ui.txt_email.setText(user['email'])

            # Get name's role
            role_name = self.roles_controller.get_role(
                self.auth_manager.token, user.get("role_id")
            ).get("name")
            # Set the role in the combobox
            self.ui.cmb_role.setCurrentText(role_name)

        else:
            self.setWindowTitle("Añadir usuario")
            self.ui.btn_save.setText("Añadir")
            self.ui.btn_reset_password.setText("Generar contraseña")

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
                response = self.users_controller.update_user(
                    self.auth_manager.token, user
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
                response = self.users_controller.add_user(self.auth_manager.token, user)
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
                        f"No se ha podido añadir el usuario. {":" + response['error'] if response else ""}",
                    )

    def set_password(self, password):
        self.password = password

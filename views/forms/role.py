from controllers import (
    AuthManager,
    RolesController,
    PermissionsController,
)
from lib.exceptions import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QDialog, QMessageBox, QListWidgetItem
from views.forms_py.role import Ui_frm_role


class frm_role(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, role_id):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.roles_controller = RolesController()
        self.permissions_controller = PermissionsController()

        self.frm = form
        self.edit = edit
        self.role_id = role_id
        self.ui = Ui_frm_role()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_add_permission.clicked.connect(self.add_permission)
        self.ui.btn_remove_permission.clicked.connect(self.remove_permission)

        # Get all permissions
        permissions = self.permissions_controller.get_permissions(
            self.auth_manager.token
        )

        if edit:
            # Rename window title
            self.setWindowTitle("Editar rol")
            # Rename the save button
            self.ui.btn_save.setText("Guardar")
            # Get role to edit
            role = self.roles_controller.get_role(self.auth_manager.token, role_id)
            # Fill in the fields
            self.ui.txt_name.setText(role.get("name"))
            self.ui.txt_description.setText(role.get("description"))
            # Get role's permissions
            role_permissions = self.roles_controller.get_permissions_id_from_role(
                self.auth_manager.token, role_id
            )
            # Add permissions in the QListViews
            for permission in permissions:
                # Not insert the total control permission
                if permission.get("code") != "CT":
                    if permission.get("code") in role_permissions:
                        self.insert_user_permission(permission)
                    else:
                        self.insert_available_permission(permission)
        else:
            # Rename window title
            self.setWindowTitle("Añadir rol")
            # Rename the save button
            self.ui.btn_save.setText("Añadir")
            # Add permissions in the QListViews
            for permission in permissions:
                # Not insert the total control permission
                if permission.get("code") != "CT":
                    self.insert_available_permission(permission)
        self.sort_permissions()

    def add_permission(self):
        selected_items = self.ui.listWidget_available_permissions.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        permission_code = selected_item.data(Qt.ItemDataRole.UserRole)
        permission = self.permissions_controller.get_permission(
            self.auth_manager.token, permission_code
        )
        self.insert_user_permission(permission)
        row = self.ui.listWidget_available_permissions.row(selected_items[0])
        self.ui.listWidget_available_permissions.takeItem(row)
        self.sort_permissions()

    def collect_rol_data(self):
        return {
            "id": self.role_id,
            "name": self.ui.txt_name.text(),
            "description": self.ui.txt_description.text(),
            "permissions": [
                self.ui.listWidget_user_permissions.item(i).data(
                    Qt.ItemDataRole.UserRole
                )
                for i in range(self.ui.listWidget_user_permissions.count())
            ],
        }

    def insert_available_permission(self, permission):
        item = QListWidgetItem(permission.get("name"))
        item.setData(Qt.ItemDataRole.UserRole, permission.get("code"))
        self.ui.listWidget_available_permissions.addItem(item)

    def insert_user_permission(self, permission):
        item = QListWidgetItem(permission.get("name"))
        item.setData(Qt.ItemDataRole.UserRole, permission.get("code"))
        self.ui.listWidget_user_permissions.addItem(item)

    def remove_permission(self):
        selected_items = self.ui.listWidget_user_permissions.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        permission_code = selected_item.data(Qt.ItemDataRole.UserRole)
        permission = self.permissions_controller.get_permission(
            self.auth_manager.token, permission_code
        )
        self.insert_available_permission(permission)
        row = self.ui.listWidget_user_permissions.row(selected_items[0])
        self.ui.listWidget_user_permissions.takeItem(row)
        self.sort_permissions()

    def sort_permissions(self):
        self.ui.listWidget_available_permissions.sortItems()
        self.ui.listWidget_user_permissions.sortItems()

    def save(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_name.text():
            QMessageBox.information(self, " ", "El nombre del rol no puede estar vacío")
            return
        if self.ui.listWidget_user_permissions.count() == 0:
            QMessageBox.information(
                self,
                " ",
                "El rol debe tener al menos un permiso asignado",
            )
            return
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                role = self.collect_rol_data()
                response = self.roles_controller.update_role(
                    self.auth_manager.token,
                    role,
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido añadir el rol{": " + response["error"] if response else "."}",
                    )
        else:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres añadir el rol?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                # Add role
                role = self.collect_rol_data()
                response = self.roles_controller.add_role(
                    self.auth_manager.token,
                    role,
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    QMessageBox.information(
                        self,
                        " ",
                        "Rol creado correctamente.",
                    )
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido añadir el rol{": " + response["error"] if response else "."}",
                    )

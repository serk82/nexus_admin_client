from .company import frm_company
from .role import frm_role
from .user import frm_user
from .permission import frm_permission
from controllers import (
    AuthManager,
    CompaniesController,
    PermissionsController,
    RolesController,
    UsersController,
)
from lib.exceptions import *
from lib.task_thread import TaskThread, LoadingDialog
from PyQt6.QtWidgets import QDialog, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.forms_py import Ui_frm_table_view


class frm_table_view(QDialog):
    def __init__(self, form, auth_manager: AuthManager, table, company_id=None):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.companies_controller = CompaniesController()
        self.permissions_controller = PermissionsController()
        self.roles_controller = RolesController()
        self.users_controller = UsersController()

        self.company_id = company_id
        self.table = table
        self.ui = Ui_frm_table_view()
        self.ui.setupUi(self)

        # Configuration based on table
        self.configuration_based_on_table()
        # Remove bold from column titles when selected
        self.ui.table_view.horizontalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: normal; }"
        )

        # Hide index of rows
        self.ui.table_view.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Sets that multiple lines can't be selected
        self.ui.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_edit.clicked.connect(self.edit)
        self.ui.btn_delete.clicked.connect(self.delete)
        if not table == "permissions":
            self.ui.table_view.doubleClicked.connect(self.edit)

    def configuration_based_on_table(self):

        self.model = QStandardItemModel()
        # Add model on table view
        self.ui.table_view.setModel(self.model)

        match self.table:
            case "companies":
                table_es = "empresas"
                self.model.setHorizontalHeaderLabels(["ID", "C.I.F.", "Empresa"])
                # Set height and width of columns
                self.ui.table_view.setColumnWidth(0, 50)
                self.ui.table_view.setColumnWidth(1, 100)
                self.ui.table_view.setColumnWidth(2, 300)
                self.ui.table_view.setFixedWidth(452)
                self.ui.table_view.setMinimumHeight(300)
            case "users":
                table_es = "usuarios"
                self.model.setHorizontalHeaderLabels(["ID", "Usuario", "Rol"])
                # Set height and width of columns
                self.ui.table_view.setColumnWidth(0, 50)
                self.ui.table_view.setColumnWidth(1, 200)
                self.ui.table_view.setColumnWidth(2, 200)
                self.ui.table_view.setFixedWidth(452)
                self.ui.table_view.setMinimumHeight(300)
            case "roles":
                table_es = "roles"
                self.model.setHorizontalHeaderLabels(["ID", "Rol", "Descripción"])
                # Set height and width of columns
                self.ui.table_view.setColumnWidth(0, 50)
                self.ui.table_view.setColumnWidth(1, 200)
                self.ui.table_view.setColumnWidth(2, 400)
                self.ui.table_view.setFixedWidth(652)
                self.ui.table_view.setMinimumHeight(300)
            case "permissions":
                table_es = "permisos"
                self.model.setHorizontalHeaderLabels(["ID", "Permiso"])
                # Set height and width of columns
                self.ui.table_view.setColumnWidth(0, 50)
                self.ui.table_view.setColumnWidth(1, 350)
                self.ui.table_view.setFixedWidth(416)
                self.ui.table_view.setMinimumHeight(300)
                self.ui.btn_add.setVisible(False)
                self.ui.btn_edit.setVisible(False)
                self.ui.btn_delete.setVisible(False)
        # Update users on table view
        self.on_update()
        # Add window title
        self.setWindowTitle(f"Administración de {table_es}")

    def on_update(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.update)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.on_task_finished)
        self.hilo.start()

    def handle_error(self, error_message):
        # Función para manejar errores
        QMessageBox.warning(self, "Error", error_message)

    def on_task_finished(self):
        self.loading_dialog.close()
        self.setEnabled(True)

    def add(self):
        self.auth_manager.is_token_expired(self)
        match self.table:
            case "companies":
                self.form = frm_company(self, self.auth_manager, False, None)
            case "permissions":
                self.form = frm_permission(self, False, None)
            case "users":
                self.form = frm_user(self, self.auth_manager, False, None)
            case "roles":
                self.form = frm_role(self, self.auth_manager, False, None)
        self.form.data_update.connect(self.on_update)
        self.form.exec()

    def edit(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_id()
        if selected_id is not None:
            match self.table:
                case "companies":
                    self.form = frm_company(self, self.auth_manager, True, selected_id)
                case "permissions":
                    self.form = frm_permission(self, True, selected_id)
                case "users":
                    self.form = frm_user(self, self.auth_manager, True, selected_id)
                case "roles":
                    if selected_id == "1":
                        QMessageBox.warning(
                            self, " ", "No se puede editar el rol de Administrador!"
                        )
                        return
                    self.form = frm_role(self, self.auth_manager, True, selected_id)
            self.form.data_update.connect(self.on_update)
            self.form.exec()
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def delete(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_id()
        if selected_id is not None:
            match self.table:
                case "companies":
                    answer = QMessageBox.question(
                        self,
                        " ",
                        "Seguro quieres eliminar la empresa?",
                        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                    )
                    if answer == QMessageBox.StandardButton.Yes:
                            if self.companies_controller.delete_company(self.auth_manager.token, selected_id):
                                self.on_update()
                            else:
                                QMessageBox.warning(
                                    self, " ", "No se ha eliminado la empresa."
                                )
                case "permissions":
                    answer = QMessageBox.question(
                        self,
                        " ",
                        "Seguro quieres eliminar el permiso?",
                        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                    )
                    if answer == QMessageBox.StandardButton.Yes:
                        try:
                            if self.permissions_controller.delete_permission(
                                selected_id
                            ):
                                self.on_update()
                            else:
                                QMessageBox.warning(
                                    self, " ", "No se ha eliminado el permiso."
                                )
                        except ValueError as e:
                            QMessageBox.warning(self, " ", str(e))
                case "users":
                    answer = QMessageBox.question(
                        self,
                        " ",
                        "Seguro quieres eliminar el usuario?",
                        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                    )
                    if answer == QMessageBox.StandardButton.Yes:
                        try:
                            self.users_controller.delete_user(int(selected_id))
                            self.on_update()
                        except DeleteError as e:
                            QMessageBox.warning(self, " ", str(e))
                        except NotFoundError as e:
                            QMessageBox.warning(self, " ", str(e))
                case "roles":
                    answer = QMessageBox.question(
                        self,
                        " ",
                        "Seguro quieres eliminar el rol?",
                        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                    )
                    if answer == QMessageBox.StandardButton.Yes:
                        if not self.users_controller.some_user_has_role(
                            self.auth_manager.token,
                            selected_id,
                        ):
                            self.roles_controller.delete_role(
                                self.auth_manager.token,
                                selected_id,
                            )
                            self.on_update()
                        else:
                            QMessageBox.warning(
                                self,
                                " ",
                                "No se puede eliminar el rol, hay usuarios asignados a él.",
                            )
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def get_selected_id(self):
        selected_index = self.ui.table_view.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.table_view.model().index(row, column).data()
        else:
            return None

    def update(self):
        self.model.removeRows(0, self.model.rowCount())
        match self.table:
            case "companies":
                companies = self.companies_controller.get_companies(
                    self.auth_manager.token
                )
                for company in companies:
                    row = [
                        QStandardItem(str(company.get("id"))),
                        QStandardItem(company.get("id_code")),
                        QStandardItem(company.get("name")),
                    ]
                    self.model.appendRow(row)
            case "permissions":
                permissions = self.permissions_controller.get_permissions(
                    self.auth_manager.token
                )
                for permission in permissions:
                    row = [
                        QStandardItem(str(permission.get("id"))),
                        QStandardItem(permission.get("name")),
                    ]
                    self.model.appendRow(row)
            case "users":
                self.users_controller = UsersController()
                users = self.users_controller.get_users(self.auth_manager.token)
                for user in users:
                    role_name = self.roles_controller.get_role(
                        self.auth_manager.token, user.get("role_id")
                    ).get("name")
                    row = [
                        QStandardItem(str(user.get("id"))),
                        QStandardItem(user.get("username")),
                        QStandardItem(role_name),
                    ]
                    self.model.appendRow(row)
            case "roles":
                roles = self.roles_controller.get_roles(self.auth_manager.token)
                for role in roles:
                    row = [
                        QStandardItem(str(role.get("id"))),
                        QStandardItem(role.get("name")),
                        QStandardItem(role.get("description")),
                    ]
                    self.model.appendRow(row)

from controllers import (
    AuthManager,
    PermissionsController,
)
from lib.exceptions import *
from lib.task_thread import TaskThread, LoadingDialog
from PyQt6.QtWidgets import QDialog, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from reports.permissions import generate_pdf
from views.forms_py import Ui_frm_permissions


class frm_permissions(QDialog):
    def __init__(self, form, auth_manager: AuthManager):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.permissions_controller = PermissionsController()
        self.ui = Ui_frm_permissions()
        self.ui.setupUi(self)

        # Add window title
        self.setWindowTitle(f"Listado de Permisos")
        # Configuration based on table
        self.configuration_based_on_table()
        # Remove bold from column titles when selected
        self.ui.tvw_permissions.horizontalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: normal; }"
        )

        # Hide index of rows
        self.ui.tvw_permissions.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_permissions.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Sets that multiple lines can't be selected
        self.ui.tvw_permissions.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_print.clicked.connect(self.print)

    def configuration_based_on_table(self):

        self.model = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_permissions.setModel(self.model)
        self.model.setHorizontalHeaderLabels(["Code", "Permiso"])
        # Set height and width of columns
        self.ui.tvw_permissions.setColumnWidth(0, 50)
        self.ui.tvw_permissions.setColumnWidth(1, 350)
        self.ui.tvw_permissions.setFixedWidth(416)
        self.ui.tvw_permissions.setMinimumHeight(400)
        # Update users on table view
        self.on_update()

    def on_update(self):
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

    def get_selected_id(self):
        selected_index = self.ui.tvw_permissions.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_permissions.model().index(row, column).data()
        else:
            return None

    def update(self):
        self.model.removeRows(0, self.model.rowCount())
        permissions = self.permissions_controller.get_permissions(
            self.auth_manager.token
        )
        for permission in permissions:
            row = [
                QStandardItem(str(permission.get("code"))),
                QStandardItem(permission.get("name")),
            ]
            self.model.appendRow(row)
            
    def print(self):
        permissions = self.permissions_controller.get_permissions(
            self.auth_manager.token
        )
        if not permissions:
            QMessageBox.warning(self, "Error", "No hay permisos para imprimir.")
            return
        filename = "informe.pdf"
        generate_pdf(filename, permissions)
        
    def on_print(self):
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.print)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.on_task_finished)
        self.hilo.start()
from controllers import (
    AuthManager,
    VehicleDocumentsController,
)
from lib.exceptions import *
from lib.task_thread import TaskThread, LoadingDialog
from PyQt6.QtWidgets import QDialog, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.forms_py import Ui_frm_vehicle_documents


class frm_document_types(QDialog):
    def __init__(self, form, auth_manager: AuthManager):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.permissions_controller = VehicleDocumentsController()
        self.ui = Ui_frm_vehicle_documents()
        self.ui.setupUi(self)

        # Add window title
        self.setWindowTitle(f"Tipos de Documento")
        # Configuration based on table
        self.configuration_based_on_table()
        # Remove bold from column titles when selected
        self.ui.tvw_vehicle_documents.horizontalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: normal; }"
        )

        # Hide index of rows
        self.ui.tvw_vehicle_documents.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_vehicle_documents.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )
        # Sets that multiple lines can't be selected
        self.ui.tvw_vehicle_documents.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )

        # Events
        self.ui.btn_close.clicked.connect(self.close)

    def configuration_based_on_table(self):

        self.model = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_vehicle_documents.setModel(self.model)
        self.model.setHorizontalHeaderLabels(["ID", "Nombre Documento"])
        # Set height and width of columns
        self.ui.tvw_vehicle_documents.setColumnWidth(0, 50)
        self.ui.tvw_vehicle_documents.setColumnWidth(1, 350)
        self.ui.tvw_vehicle_documents.setFixedWidth(416)
        self.ui.tvw_vehicle_documents.setMinimumHeight(400)
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
        selected_index = (
            self.ui.tvw_vehicle_documents.selectionModel().selectedIndexes()
        )
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_vehicle_documents.model().index(row, column).data()
        else:
            return None

    def update(self):
        self.model.removeRows(0, self.model.rowCount())
        permissions = self.permissions_controller.get_vehicle_documents(
            self.auth_manager.token
        )
        for permission in permissions:
            row = [
                QStandardItem(str(permission.get("id"))),
                QStandardItem(permission.get("name")),
            ]
            self.model.appendRow(row)

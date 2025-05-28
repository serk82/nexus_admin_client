from controllers import (
    AuthManager,
    TypesVehicleDocumentsController,
)
from lib.exceptions import *
from lib.task_thread import TaskThread, LoadingDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QTableView, QMessageBox
from views.forms_py import Ui_frm_types_vehicle_documents


class frm_types_vehicle_documents(QDialog):

    def __init__(self, form, auth_manager: AuthManager):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.vehicle_documents = TypesVehicleDocumentsController()
        self.ui = Ui_frm_types_vehicle_documents()
        self.ui.setupUi(self)

        # Add window title
        self.setWindowTitle(f"Tipos de Documento")
        # Configuration based on table
        self.configuration_based_on_table()
        # Remove bold from column titles when selected
        self.ui.tvw_types_vehicle_documents.horizontalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: normal; }"
        )

        # Hide index of rows
        self.ui.tvw_types_vehicle_documents.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_types_vehicle_documents.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )
        # Sets that multiple lines can't be selected
        self.ui.tvw_types_vehicle_documents.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_edit.clicked.connect(self.edit)
        self.ui.tvw_types_vehicle_documents.doubleClicked.connect(self.edit)
        self.ui.btn_delete.clicked.connect(self.delete)

    def add(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_type_vehicle_document

        form = frm_type_vehicle_document(self, self.auth_manager, False, None)
        form.data_update.connect(self.on_update)
        form.exec()

    def configuration_based_on_table(self):

        self.model = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_types_vehicle_documents.setModel(self.model)
        self.model.setHorizontalHeaderLabels(["ID", "Nombre Documento"])
        # Set height and width of columns
        self.ui.tvw_types_vehicle_documents.setColumnWidth(0, 50)
        self.ui.tvw_types_vehicle_documents.setColumnWidth(1, 350)
        self.ui.tvw_types_vehicle_documents.setFixedWidth(402)
        self.ui.tvw_types_vehicle_documents.setMinimumHeight(400)
        # Update users on table view
        self.on_update()

    def delete(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_id()
        if not selected_id:
            QMessageBox.information(
                self, " ", "No hay ningun tipo de documento seleccionado."
            )
            return
        response = self.vehicle_documents.delete_type_vehicle_document(
            self.auth_manager.token, selected_id
        )
        if response and "error" not in response:
            QMessageBox.information(
                self, " ", "Tipo de documento eliminado correctamente."
            )
            self.on_update()
        else:
            QMessageBox.warning(
                self,
                " ",
                f"No se ha podido eliminar el tipo de documento{': ' + response['error'] if response else '.'}",
            )

    def edit(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_type_vehicle_document

        selected_id = self.get_selected_id()
        if not selected_id:
            QMessageBox.information(
                self, " ", "No hay ningun tipo de documento seleccionado."
            )
            return
        form = frm_type_vehicle_document(self, self.auth_manager, True, selected_id)
        form.data_update.connect(self.on_update)
        form.exec()

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
            self.ui.tvw_types_vehicle_documents.selectionModel().selectedIndexes()
        )
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_types_vehicle_documents.model().index(row, column).data()
        else:
            return None

    def update(self):
        self.model.removeRows(0, self.model.rowCount())
        permissions = self.vehicle_documents.get_types_vehicle_documents(
            self.auth_manager.token
        )
        for permission in permissions:
            row = [
                QStandardItem(str(permission.get("id"))),
                QStandardItem(permission.get("name")),
            ]
            self.model.appendRow(row)

import json, os, requests, sys, subprocess, webbrowser
from controllers import AuthManager, WorkOrdersController
from datetime import date, datetime
from lib.config import API_HOST, API_PORT
from lib.task_thread import *
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QMessageBox, QHeaderView, QTableView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSignal
from views.forms_py import Ui_frm_workorder


class frm_workorder(QDialog):

    data_update_workorder = pyqtSignal()

    def __init__(
        self,
        form,
        auth_manager: AuthManager,
        edit,
        workorder_id,
        vehicle_id,
        company_id,
    ):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.ui = Ui_frm_workorder()
        self.ui.setupUi(self)

        # Drag and drop
        self.ui.lbl_dragdrop.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop.dropEvent = self.dropEvent

        # Variables
        self.workorders_controller = WorkOrdersController()
        self.company_id = company_id
        self.vehicle_id = vehicle_id
        self.workorder_id = workorder_id
        self.path = f"{self.company_id}/vehicles/{self.vehicle_id}/workorders/{self.workorder_id}"
        self.edit = edit

        self.configuration_based_on_documents()

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_delete_document.clicked.connect(self.on_delete_document)
        self.ui.btn_view_document.clicked.connect(self.open_document)
        self.ui.tvw_documents.doubleClicked.connect(self.open_document)

        # Check Permissions
        if not self.auth_manager.has_permission("EMV"):
            self.ui.date_workorder.setReadOnly(True)
            self.ui.txt_realized_by.setReadOnly(True)
            self.ui.txt_description.setReadOnly(True)
            self.ui.btn_view_document.setEnabled(
                self.auth_manager.has_permission("VDV")
            )
            self.ui.btn_delete_document.setEnabled(
                self.auth_manager.has_permission("DEV")
            )
            self.ui.lbl_dragdrop.setEnabled(self.auth_manager.has_permission("EMV"))
            self.ui.btn_save.setEnabled(False)

        if self.edit:
            self.load_edit()
        else:
            self.load_add()

    def add(self):
        workorder = self.collect_workorder_data()
        response = self.workorders_controller.add_workorder(
            self.auth_manager.token, workorder
        )
        if "error" in response:
            raise Exception(response.get("error"))
        self.workorder_id = response.get("workorder_id")

    def cleanup_tmp(self):
        tmp_dir = Path(sys.argv[0]).resolve().parent / "tmp"
        if tmp_dir.exists() and tmp_dir.is_dir():
            for f in tmp_dir.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        " ",
                        f"No se pudo eliminar el archivo temporal:\n{e}",
                    )

    # Llama a esto al cerrar
    def closeEvent(self, event):
        self.cleanup_tmp()
        event.accept()

    def collect_workorder_data(self):
        return {
            "id": self.workorder_id if self.workorder_id else None,
            "date": date(
                self.ui.date_workorder.date().year(),
                self.ui.date_workorder.date().month(),
                self.ui.date_workorder.date().day(),
            ).isoformat(),
            "realized_by": self.ui.txt_realized_by.text(),
            "description": self.ui.txt_description.toPlainText(),
            "vehicle_id": self.vehicle_id,
        }

    def configuration_based_on_documents(self):
        # Hide index of rows
        self.ui.tvw_documents.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_documents.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Sets that multiple lines can't be selected
        self.ui.tvw_documents.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.ui.tvw_documents.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.model_documents = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_documents.setModel(self.model_documents)
        self.model_documents.setHorizontalHeaderLabels(
            [
                "Nombre documento",
            ]
        )
        self.ui.tvw_documents.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.ui.tvw_documents.horizontalHeader().hide()

    def delete_document(self):
        self.workorders_controller.delete_document(
            self.auth_manager.token,
            self.path,
            self.get_selected_document(),
        )

    def download_file_to_tmp(self, filename: str, url: str) -> Path:
        response = requests.get(url)
        response.raise_for_status()

        file_path = self.path / filename
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = Path(urls[0].toLocalFile())
            if file_path.is_file():
                if (
                    str(file_path).endswith(".pdf")
                    or str(file_path).endswith(".PDF")
                    or str(file_path).endswith(".png")
                    or str(file_path).endswith(".PNG")
                    or str(file_path).endswith(".jpg")
                    or str(file_path).endswith(".JPG")
                    or str(file_path).endswith(".jpeg")
                    or str(file_path).endswith(".JPEG")
                ):
                    try:
                        if self.exist_document(file_path.name):
                            QMessageBox.warning(
                                self,
                                " ",
                                f"El documento '{file_path.name}' ya existe.",
                            )
                            return
                        self.upload_file(file_path)
                        self.model_documents.appendRow(
                            [
                                QStandardItem(file_path.name),
                            ]
                        )
                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"No se pudo subir el archivo:\n{e}",
                        )
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        "El archivo no es un documento válido.\n"
                        "Por favor, sube un archivo PDF o de imagen.",
                    )

    def exist_document(self, filename):
        for row in range(self.model_documents.rowCount()):
            item = self.model_documents.item(row, 0)
            if item and item.text() == filename:
                return True
        return False

    def get_selected_document(self):
        selected_index = self.ui.tvw_documents.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_documents.model().index(row, column).data()
        else:
            return None

    def handle_error(self, error_message):
        # Función para manejar errores
        self.loading_dialog.close()
        QMessageBox.warning(self, " ", error_message)
        self.setEnabled(True)

    def load_add(self):
        self.ui.gbx_documents.setEnabled(False)
        self.ui.btn_save.clicked.connect(self.on_add_clicked)
        self.setWindowTitle("Añadir orden de trabajo")
        self.ui.btn_save.setText("Añadir")
        self.ui.date_workorder.setDate(date.today())

    def load_documents(self):
        self.model_documents.removeRows(0, self.model_documents.rowCount())
        documents = self.workorders_controller.get_documents(
            self.auth_manager.token,
            self.path,
        )
        if documents:
            for document in documents:
                self.model_documents.appendRow([QStandardItem(document)])

    def load_edit(self):
        self.ui.btn_save.disconnect()
        self.ui.btn_save.clicked.connect(self.on_save_clicked)
        self.setWindowTitle("Editar orden de trabajo")
        self.ui.btn_save.setText("Guardar")
        self.load_workorder()

    def load_workorder(self):
        workorder = self.workorders_controller.get_workorder(
            self.auth_manager.token, self.workorder_id
        )
        self.load_documents()
        date = datetime.strptime(workorder.get("date"), "%Y-%m-%d")
        self.ui.date_workorder.setDate(date)
        self.ui.txt_realized_by.setText(workorder.get("realized_by"))
        self.ui.txt_description.setPlainText(workorder.get("description"))

    def on_add_clicked(self):
        self.auth_manager.is_token_expired(self)
        answer = QMessageBox.question(
            self,
            " ",
            "Seguro quieres añadir la orden de trabajo?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.setEnabled(False)
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()
            self.hilo = TaskThread(self.add)
            self.hilo.error.connect(self.handle_error)
            self.hilo.finished.connect(self.on_task_finished)
            self.hilo.start()

    def on_delete_document(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_document()
        if selected_id is not None:
            answer = QMessageBox.question(
                self,
                " ",
                f"Seguro quieres elimninar el documento '{selected_id}'?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.setEnabled(False)
                self.loading_dialog = LoadingDialog(self)
                self.loading_dialog.show()
                self.hilo = TaskThread(self.delete_document)
                self.hilo.error.connect(self.handle_error)
                self.hilo.finished.connect(self.on_task_delete_document_finished)
                self.hilo.start()
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def on_file_dropped(self, file_path: Path):
        self.model_documents.appendRow(
            [
                QStandardItem(""),
                QStandardItem(file_path.name),
            ]
        )

    def on_open_document(self):
        self.auth_manager.is_token_expired(self)
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.open_document)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.on_task_open_document_finished)
        self.hilo.start()

    def on_save_clicked(self):
        self.auth_manager.is_token_expired(self)
        answer = QMessageBox.question(
            self,
            " ",
            "Seguro quieres guardar los cambios?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.setEnabled(False)
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()
            self.hilo = TaskThread(self.save)
            self.hilo.error.connect(self.handle_error)
            self.hilo.finished.connect(self.on_task_finished)
            self.hilo.start()

    def on_task_delete_document_finished(self):
        self.load_documents()
        self.loading_dialog.close()
        self.setEnabled(True)

    def on_task_open_document_finished(self):
        self.loading_dialog.close()
        self.ui.gbx_documents.setEnabled(True)
        self.setEnabled(True)

    def on_task_finished(self):
        self.data_update_workorder.emit()
        self.loading_dialog.close()
        if self.edit:
            self.close()
        self.ui.gbx_documents.setEnabled(True)
        self.load_edit()
        self.edit = True
        self.setEnabled(True)

    def open_document(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_document()
        if selected_id is not None:
            response = self.workorders_controller.get_file(
                self.auth_manager.token,
                self.path,
                selected_id,
            )
            try:
                file_path = Path(sys.argv[0]).resolve().parent / "tmp" / selected_id
                with open(file_path, "wb") as f:
                    f.write(response)
                self.open_file(file_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    " ",
                    f"No se pudo abrir el archivo:\n{e}",
                )
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def open_file(self, file_path):
        if (
            str(file_path).endswith(".pdf")
            or str(file_path).endswith(".PDF")
            or str(file_path).endswith(".png")
            or str(file_path).endswith(".PNG")
            or str(file_path).endswith(".jpg")
            or str(file_path).endswith(".JPG")
            or str(file_path).endswith(".jpeg")
            or str(file_path).endswith(".JPEG")
        ):
            webbrowser.open(str(file_path))
            return

    def save(self):
        workorder = self.collect_workorder_data()
        self.workorders_controller.update_workorder(self.auth_manager.token, workorder)

    def upload_file(self, file_path: Path):
        url = f"http://{API_HOST}:{API_PORT}/files/"
        subfolder = f"{self.company_id}/vehicles/{self.vehicle_id}/workorders/{self.workorder_id}"

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                data = {"subfolder": subfolder}
                response = requests.post(url, files=files, data=data)

            if not response.ok:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error del servidor: {response.status_code}\n{response.text}",
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo subir el archivo:\n{e}")

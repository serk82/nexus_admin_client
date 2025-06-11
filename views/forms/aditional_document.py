import sys
from controllers import (
    AuthManager,
    FilesController,
)
from lib.exceptions import *
from pathlib import Path
from shutil import copyfile
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py.aditional_document import Ui_frm_aditional_document


class frm_aditional_document(QDialog):

    data_update_documents = pyqtSignal()

    def __init__(
        self,
        form,
        auth_manager: AuthManager,
        edit,
        vehicle_id,
        company_id,
        document,
    ):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.files_controller = FilesController()

        self.frm = form
        self.edit = edit
        self.vehicle_id = vehicle_id
        self.company_id = company_id
        self.document = document
        self.path = None
        self.path_subfolder_aditional_documents = (
            f"{self.company_id}/vehicles/{self.vehicle_id}/documents/aditional"
        )

        self.ui = Ui_frm_aditional_document()
        self.ui.setupUi(self)

        self.ui.lbl_dragdrop.setAcceptDrops(True)
        self.ui.lbl_dragdrop.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop.dropEvent = self.dropEventDocument

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)

        if edit:
            # Rename window title
            self.setWindowTitle("Editar documento")
            # Rename the save button
            self.ui.btn_save.setText("Guardar")
            # Fill in the fields
            document = str(self.document).split(".")
            self.ui.txt_name.setText(document[0])
            response = self.files_controller.get_file(
                self.auth_manager.token,
                self.path_subfolder_aditional_documents,
                self.document,
            )
            try:
                self.path = Path(sys.argv[0]).resolve().parent / "tmp" / self.document
                with open(self.path, "wb") as f:
                    f.write(response)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    " ",
                    f"No se pudo abrir el archivo:\n{e}",
                )
        else:
            # Rename window title
            self.setWindowTitle("Añadir documento")
            # Rename the save button
            self.ui.btn_save.setText("Añadir")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEventDocument(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        file_path = Path(urls[0].toLocalFile())
        if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
            QMessageBox.information(
                self,
                "Archivo no válido",
                "El archivo no es un documento PDF válido.\n"
                "Por favor, sube un archivo PDF.",
            )
            return
        self.path = file_path
        self.ui.lbl_path.setText(str(file_path))

    def save(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_name.text() and self.ui.txt_name.isEnabled():
            QMessageBox.information(
                self, " ", "El nombre de documento no puede estar vacío"
            )
            return
        if not self.ui.lbl_path.text() and not self.edit:
            QMessageBox.information(self, " ", "Debes añadir un archivo PDF.")
            return
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                response = self.files_controller.upload_edit_file(
                    self.auth_manager.token,
                    self.path,
                    self.path_subfolder_aditional_documents,
                    f"{self.ui.txt_name.text()}.pdf",
                    self.document,
                )
                if response and "error" not in response:
                    self.data_update_documents.emit()
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido añadir el tipo de documento{': ' + response['error'] if response else '.'}",
                    )
        else:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres añadir el documento?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                # Add vehicle_document
                response = self.files_controller.upload_file(
                    self.auth_manager.token,
                    self.path,
                    self.path_subfolder_aditional_documents,
                    f"{self.ui.txt_name.text()}.pdf",
                )
                if "error" in response:
                    QMessageBox.information(
                        self,
                        " ",
                        f"{response.get('error')}",
                    )
                    return
                self.data_update_documents.emit()
                self.close()
            else:
                QMessageBox.information(
                    self,
                    " ",
                    f"No se ha podido añadir el tipo de documento{': ' + response['error'] if response else '.'}",
                )

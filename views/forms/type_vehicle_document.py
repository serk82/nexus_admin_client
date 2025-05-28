from controllers import (
    AuthManager,
    TypesVehicleDocumentsController,
)
from lib.exceptions import *
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py.type_vehicle_document import Ui_frm_type_vehicle_document


class frm_type_vehicle_document(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, vehicle_document_id):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.vehicle_documents = TypesVehicleDocumentsController()

        self.frm = form
        self.edit = edit
        self.vehicle_document_id = vehicle_document_id
        self.ui = Ui_frm_type_vehicle_document()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)

        if edit:
            # Rename window title
            self.setWindowTitle("Editar tipo de documento")
            # Rename the save button
            self.ui.btn_save.setText("Guardar")
            # Get vehicle_document to edit
            vehicle_document = self.vehicle_documents.get_type_vehicle_document(
                self.auth_manager.token, vehicle_document_id
            )
            # Fill in the fields
            self.ui.txt_name.setText(vehicle_document.get("name"))
        else:
            # Rename window title
            self.setWindowTitle("Añadir tipo de documento")
            # Rename the save button
            self.ui.btn_save.setText("Añadir")

    def collect_rol_data(self):
        return {
            "id": self.vehicle_document_id,
            "name": self.ui.txt_name.text(),
        }

    def save(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_name.text():
            QMessageBox.information(
                self, " ", "El nombre de tipo de documento no puede estar vacío"
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
                vehicle_document = self.collect_rol_data()
                response = self.vehicle_documents.update_type_vehicle_document(
                    self.auth_manager.token,
                    vehicle_document,
                )
                if response and "error" not in response:
                    self.data_update.emit()
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
                "Seguro quieres añadir el tipo de documento?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                # Add vehicle_document
                vehicle_document = self.collect_rol_data()
                response = self.vehicle_documents.add_type_vehicle_document(
                    self.auth_manager.token,
                    vehicle_document,
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    QMessageBox.information(
                        self,
                        " ",
                        "Tipo de documento creado correctamente.",
                    )
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        f"No se ha podido añadir el tipo de documento{': ' + response['error'] if response else '.'}",
                    )

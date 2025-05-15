from controllers import AuthManager, CompaniesController
from lib.exceptions import *
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py.company import Ui_frm_company


class frm_company(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, id):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.companies_controller = CompaniesController()

        self.frm = form
        self.edit = edit
        self.id = id
        self.ui = Ui_frm_company()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)

        if edit:
            self.setWindowTitle("Editar empresa")
            self.ui.btn_save.setText("Guardar")
            company = self.companies_controller.get_company(self.auth_manager.token, id)
            self.ui.txt_id_code.setText(company.get("id_code"))
            self.ui.txt_name.setText(company.get("name"))
            self.ui.txt_address.setText(company.get("address"))
            self.ui.txt_locality.setText(company.get("locality"))
            self.ui.txt_postal_code.setText(company.get("postal_code"))
            self.ui.txt_phone.setText(company.get("phone"))
        else:
            self.setWindowTitle("Añadir empresa")
            self.ui.btn_save.setText("Añadir")

    def save(self):
        self.auth_manager.is_token_expired(self.frm)
        if not self.ui.txt_id_code.text():
            QMessageBox.warning(self, " ", "El campo 'C.I.F.' no puede estar vacío!")
            return
        if not self.ui.txt_name.text():
            QMessageBox.warning(self, " ", "El campo 'Nombre' no puede estar vacío!")
            return
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                company = self.collect_company_data()
                response = self.companies_controller.update_company(
                    self.auth_manager.token, company
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        response["error"],
                    )
        else:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres añadir la empresa?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                # Add role
                company = self.collect_company_data()
                response = self.companies_controller.add_company(
                    self.auth_manager.token, company
                )
                if response and "error" not in response:
                    self.data_update.emit()
                    self.close()
                else:
                    QMessageBox.information(
                        self,
                        " ",
                        response["error"],
                    )

    def collect_company_data(self):
        return {
            "id": self.id if self.id else None,
            "id_code": self.ui.txt_id_code.text(),
            "name": self.ui.txt_name.text(),
            "address": self.ui.txt_address.text(),
            "locality": self.ui.txt_locality.text(),
            "postal_code": self.ui.txt_postal_code.text(),
            "phone": self.ui.txt_phone.text(),
        }

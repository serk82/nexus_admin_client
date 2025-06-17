from controllers import AuthManager, InspectionsController
from datetime import date, datetime
from lib.decorators import track_user_activity
from lib.methods import *
from lib.task_thread import *
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py import Ui_frm_inspection


@track_user_activity
class frm_inspection(QDialog):

    data_update_inspections = pyqtSignal()

    def __init__(
        self, form, auth_manager: AuthManager, edit, inspection_id, vehicle_id
    ):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.ui = Ui_frm_inspection()
        self.ui.setupUi(self)

        # Set variables
        self.inspection_controller = InspectionsController()
        self.inspection_id = inspection_id
        self.vehicle_id = vehicle_id
        self.edit = edit

        # Events
        self.ui.btn_cancel.clicked.connect(self.close)

        if self.edit:
            self.ui.btn_save.clicked.connect(self.on_save_clicked)
            self.setWindowTitle("Editar revisión")
            self.ui.btn_save.setText("Guardar")
            self.load_inspection()
        else:
            self.ui.btn_save.clicked.connect(self.on_add_clicked)
            self.setWindowTitle("Añadir revisión")
            self.ui.btn_save.setText("Añadir")
            self.ui.date_inspection.setDate(date.today())

    def add(self):
        inspection = self.collect_inspection_data()
        self.inspection_controller.add_inspection(self.auth_manager.token, inspection)

    def collect_inspection_data(self):
        return {
            "id": self.inspection_id if self.inspection_id else None,
            "vehicle_id": self.vehicle_id,
            "date": date(
                self.ui.date_inspection.date().year(),
                self.ui.date_inspection.date().month(),
                self.ui.date_inspection.date().day(),
            ).isoformat(),
            "kms": self.ui.sbx_kms.value(),
            "hours": self.ui.sbx_hours.value(),
            "motor_oil": self.ui.chb_motor_oil.isChecked(),
            "transmission_oil": self.ui.chb_transmission_oil.isChecked(),
            "diferential_oil": self.ui.chb_diferential_oil.isChecked(),
            "hydraulic_oil": self.ui.chb_hydraulic_oil.isChecked(),
            "oil_filter": self.ui.chb_oil_filter.isChecked(),
            "fuel_filter": self.ui.chb_fuel_filter.isChecked(),
            "air_filter": self.ui.chb_air_filter.isChecked(),
            "poller_filter": self.ui.chb_poller_filter.isChecked(),
            "hydraulic_filter": self.ui.chb_hydraulic_filter.isChecked(),
        }

    def handle_error(self, error_message, error_details):
        # Función para manejar errores
        self.loading_dialog.close()
        show_error_dialog(self, error_message, error_details)
        self.setEnabled(True)

    def load_inspection(self):
        self.inspection = self.inspection_controller.get_inspection(
            self.auth_manager.token, self.inspection_id
        )
        date = datetime.strptime(self.inspection.get("date"), "%Y-%m-%d")
        self.ui.date_inspection.setDate(date)
        self.ui.sbx_kms.setValue(
            self.inspection.get("kms") if self.inspection.get("kms") else 0
        )
        self.ui.sbx_hours.setValue(
            self.inspection.get("hours") if self.inspection.get("hours") else 0
        )
        self.ui.chb_motor_oil.setChecked(
            True if self.inspection.get("motor_oil") else False
        )
        self.ui.chb_transmission_oil.setChecked(
            True if self.inspection.get("transmission_oil") else False
        )
        self.ui.chb_diferential_oil.setChecked(
            True if self.inspection.get("diferential_oil") else False
        )
        self.ui.chb_hydraulic_oil.setChecked(
            True if self.inspection.get("hydraulic_oil") else False
        )
        self.ui.chb_oil_filter.setChecked(
            True if self.inspection.get("oil_filter") else False
        )
        self.ui.chb_fuel_filter.setChecked(
            True if self.inspection.get("fuel_filter") else False
        )
        self.ui.chb_air_filter.setChecked(
            True if self.inspection.get("air_filter") else False
        )
        self.ui.chb_poller_filter.setChecked(
            True if self.inspection.get("poller_filter") else False
        )
        self.ui.chb_hydraulic_filter.setChecked(
            True if self.inspection.get("hydraulic_filter") else False
        )

    def on_add_clicked(self):
        self.auth_manager.is_token_expired(self)
        if self.ui.sbx_kms.value() == 0:
            QMessageBox.warning(
                self, " ", "Los KMS no pueden ser 0", QMessageBox.StandardButton.Ok
            )
            return
        answer = QMessageBox.question(
            self,
            " ",
            "Seguro quieres añadir la revisión?",
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

    def on_task_finished(self):
        self.data_update_inspections.emit()
        self.close()

    def save(self):
        inspection = self.collect_inspection_data()
        self.inspection_controller.update_inspection(
            self.auth_manager.token, inspection
        )

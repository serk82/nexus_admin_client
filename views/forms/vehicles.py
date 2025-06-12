from .vehicle import frm_vehicle
from controllers import AuthManager, VehiclesController
from lib.decorators import track_user_activity
from lib.exceptions import *
from lib.methods import get_kms_vehicles, get_format_miles
from lib.task_thread import TaskThread, LoadingDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QTableView, QMessageBox, QHeaderView
from views.forms_py import Ui_frm_vehicles


@track_user_activity
class frm_vehicles(QDialog):

    def __init__(self, form, auth_manager: AuthManager, company_id=None):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.vehicles_controller = VehiclesController()

        self.company_id = company_id
        self.table = "vehicles"
        self.ui = Ui_frm_vehicles()
        self.ui.setupUi(self)

        # Default
        self.ui.rad_actives.setChecked(True)
        self.searching = False

        # Configuration based on table
        self.configuration_based_on_table()

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_view.clicked.connect(self.edit)
        self.ui.btn_delete.clicked.connect(self.delete)
        self.ui.tvw_vehicles.doubleClicked.connect(self.edit)
        self.ui.rad_actives.clicked.connect(self.on_update)
        self.ui.rad_disabled.clicked.connect(self.on_update)
        self.ui.rad_all.clicked.connect(self.on_update)
        self.ui.txt_search.returnPressed.connect(self.on_search)

        # Check permissions
        self.ui.btn_add.setEnabled(self.auth_manager.has_permission("AV"))
        self.ui.btn_delete.setEnabled(self.auth_manager.has_permission("DV"))

    def add(self):
        self.form = frm_vehicle(self, self.auth_manager, False, None, self.company_id)
        self.form.data_update.connect(self.on_update)
        self.form.exec()

    def configuration_based_on_table(self):
        # Hide index of rows
        self.ui.tvw_vehicles.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_vehicles.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Sets that multiple lines can't be selected
        self.ui.tvw_vehicles.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.ui.tvw_vehicles.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.ui.tvw_vehicles.resizeColumnsToContents()
        self.model = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_vehicles.setModel(self.model)
        table_es = "vehículos"
        self.model.setHorizontalHeaderLabels(
            ["ID", "Alias", "Matrícula", "Marca y modelo", "KMS Actuales"]
        )
        self.ui.tvw_vehicles.setColumnHidden(0, True)
        self.ui.tvw_vehicles.setAlternatingRowColors(True)
        # Set height and width of columns
        header = self.ui.tvw_vehicles.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Update users on table view
        self.on_update()
        # Add window title
        self.setWindowTitle(f"Administración de {table_es}")

    def edit(self):
        selected_id = self.get_selected_id()
        if selected_id is not None:
            try:
                self.form = frm_vehicle(
                    self, self.auth_manager, True, selected_id, self.company_id
                )
                self.form.data_update.connect(self.on_update)
                self.form.exec()
            except Exception as e:
                QMessageBox.warning(self, " ", f"Error: {e}")
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def delete(self):
        selected_id = self.get_selected_id()
        if selected_id is not None:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres eliminar el vehículo?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                response = self.vehicles_controller.delete_vehicle(
                    self.auth_manager.token, selected_id
                )
                if "error" in response:
                    QMessageBox.warning(self, " ", response.get("error"))
                self.on_update()

    def get_selected_id(self):
        selected_index = self.ui.tvw_vehicles.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_vehicles.model().index(row, column).data()
        else:
            return None

    def handle_error(self, error_message):
        # Función para manejar errores
        self.loading_dialog.close()
        QMessageBox.warning(self, "Error", error_message)

    def on_search(self):
        self.on_update()
        self.searching = True

    def on_task_finished(self):
        self.loading_dialog.close()
        self.setEnabled(True)
        if self.searching:
            self.ui.txt_search.setFocus()
            self.searching = False

    def on_update(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.update)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.on_task_finished)
        self.hilo.start()

    def update(self):
        self.model.removeRows(0, self.model.rowCount())
        if self.ui.rad_actives.isChecked():
            data = self.vehicles_controller.get_vehicles(
                self.auth_manager.token,
                self.company_id,
                False,
                self.ui.txt_search.text(),
            )
        if self.ui.rad_disabled.isChecked():
            data = self.vehicles_controller.get_vehicles(
                self.auth_manager.token,
                self.company_id,
                True,
                self.ui.txt_search.text(),
            )
        if self.ui.rad_all.isChecked():
            data = self.vehicles_controller.get_vehicles(
                self.auth_manager.token,
                self.company_id,
                None,
                self.ui.txt_search.text(),
            )
        all_current_kms = get_kms_vehicles()
        for item in data:
            current_kms = "0"
            for vehicle in all_current_kms.findall("GRUA"):
                if vehicle.find("MATRICULA").text == item.get("license_plate"):
                    current_kms = get_format_miles(vehicle.find("KMS").text)
                    break
            row = [
                QStandardItem(str(item.get("id"))),
                QStandardItem(item.get("alias")),
                QStandardItem(item.get("license_plate")),
                QStandardItem(item.get("brand") + " " + item.get("model")),
                QStandardItem("" if current_kms == "0" else current_kms),
            ]
            self.model.appendRow(row)

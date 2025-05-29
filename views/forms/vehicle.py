import requests, sys
from controllers import (
    AuthManager,
    FilesController,
    InspectionsController,
    VehiclesController,
    VehicleDocumentsController,
    WorkOrdersController,
)
from datetime import date, datetime
from lib.config import API_HOST, API_PORT
from lib.exceptions import *
from lib.methods import *
from lib.task_thread import *
from pathlib import Path
from shutil import copyfile
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableView,
    QHeaderView,
    QFileDialog,
)
from views.forms_py import Ui_frm_vehicle


class frm_vehicle(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, id, company_id):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.files_controller = FilesController()
        self.inspections_controller = InspectionsController()
        self.vehicles_controller = VehiclesController()
        self.vehicle_documents_controlles = VehicleDocumentsController()
        self.workorders_controller = WorkOrdersController()
        self.frm_users = form
        self.edit = edit
        self.id = id
        self.company_id = company_id
        self.vehicle = None
        self.inspections = None
        self.last_inspection = None
        self.workorders = None
        self.first_workorder = None
        self.last_workorder = None
        self.date_first_workorder = None
        self.date_last_workorder = None
        self.date_from_workorder = None
        self.date_to_workorder = None
        self.path_image = None
        self.path_image_tmp = Path(sys.argv[0]).resolve().parent / "tmp" / "image.jpg"
        self.path_subfolder_image = f"{self.company_id}/vehicles/{self.id}/photos/image"
        self.ui = Ui_frm_vehicle()
        self.ui.setupUi(self)

        self.is_adding = False
        self.is_editing = False

        self.configuration_tableviews()
        self.configuration_based_on_inspections()
        self.configuration_based_on_vehicle_documents()
        self.configuration_based_on_workorders()

        # Events
        self.ui.btn_edit.clicked.connect(self.enable_form_fields)
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_image.clicked.connect(self.change_image)
        self.ui.chb_tachograph_expiry.stateChanged.connect(self.check_tachograph_expery)
        self.ui.chb_itv_expiry.stateChanged.connect(self.check_itv_expery)
        self.ui.chb_inspection_km.stateChanged.connect(self.check_inspection_km)
        self.ui.chb_inspection_hours.stateChanged.connect(self.check_inspection_hours)
        self.ui.sbx_inspection_km.valueChanged.connect(self.get_next_kms_inspection)
        self.ui.sbx_inspection_hours.valueChanged.connect(self.get_next_kms_inspection)

        # Buttons Tab Events
        self.ui.tab_file.tabBar().tabBarClicked.connect(self.update_tab)

        # Events for workorders
        self.ui.tvw_workorders.doubleClicked.connect(self.edit_workorder)
        self.ui.date_from.dateChanged.connect(self.change_date_from)
        self.ui.date_to.dateChanged.connect(self.change_date_to)
        self.ui.txt_search.returnPressed.connect(self.on_load_filtered_workorders)
        self.ui.btn_filter.clicked.connect(self.on_load_filtered_workorders)
        self.ui.btn_remove_filters.clicked.connect(self.remove_filters)
        self.ui.btn_add_workorder.clicked.connect(self.add_workorder)
        self.ui.btn_edit_workorder.clicked.connect(self.edit_workorder)
        self.ui.btn_delete_workorder.clicked.connect(self.delete_workorder)

        # Events for inspections
        self.ui.tvw_inspections.doubleClicked.connect(self.edit_inspection)
        self.ui.btn_add_inspection.clicked.connect(self.add_inspection)
        self.ui.btn_edit_inspection.clicked.connect(self.edit_inspection)
        self.ui.btn_delete_inspection.clicked.connect(self.delete_inspection)

        # Events for documentation
        self.ui.btn_add_aditional_document.clicked.connect(self.add_vehicle_document)

        # Check permissions
        self.ui.btn_edit.setEnabled(self.auth_manager.has_permission("EV"))
        self.ui.btn_add_inspection.setEnabled(self.auth_manager.has_permission("ARV"))
        self.ui.btn_edit_inspection.setEnabled(self.auth_manager.has_permission("ERV"))
        self.ui.btn_delete_inspection.setEnabled(
            self.auth_manager.has_permission("DRV")
        )
        self.ui.btn_add_workorder.setEnabled(self.auth_manager.has_permission("AMV"))
        if not self.auth_manager.has_permission("EMV"):
            self.ui.btn_edit_workorder.setText("Ver")
            if not self.auth_manager.has_permission("VMV"):
                self.ui.btn_edit_workorder.setEnabled(False)
        self.ui.btn_delete_workorder.setEnabled(self.auth_manager.has_permission("DMV"))

        if edit:
            self.load_edit()
        else:
            self.load_add()

    def add(self):
        vehicle = self.collect_vehicle_data()
        response = self.vehicles_controller.add_vehicle(
            self.auth_manager.token, vehicle
        )
        if "error" in response:
            raise Exception(response.get("error"))
        self.id = response.get("vehicle_id")

    def add_inspection(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_inspection

        self.form = frm_inspection(self, self.auth_manager, False, None, self.id)
        self.form.data_update_inspections.connect(self.on_load_inspections)
        self.form.exec()

    def add_registration_certificate(self):
        self.auth_manager.is_token_expired(self)
        document, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un documento PDF", "", "Archivos PDF (*.pdf)"
        )
        if document:
            QMessageBox.information(self, " ", document)

    def add_vehicle_document(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_vehicle_document

        self.form = frm_vehicle_document(
            self, self.auth_manager, False, None, self.id, self.company_id
        )
        self.form.data_update_vehicle_documents.connect(self.on_load_vehicle_documents)
        self.form.exec()

    def add_workorder(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_workorder

        self.form = frm_workorder(
            self, self.auth_manager, False, None, self.id, self.company_id
        )
        self.form.data_update_workorder.connect(self.on_load_workorders)
        self.form.exec()

    def change_date_from(self):
        self.date_from_workorder = date(
            self.ui.date_from.date().year(),
            self.ui.date_from.date().month(),
            self.ui.date_from.date().day(),
        )

    def change_date_to(self):
        self.date_to_workorder = date(
            self.ui.date_to.date().year(),
            self.ui.date_to.date().month(),
            self.ui.date_to.date().day(),
        )

    def change_image(self):
        self.auth_manager.is_token_expired(self)
        image, _ = QFileDialog.getOpenFileName(
            self, "Selecciona una imagen JPG", "", "Archivos JPG (*.jpg)"
        )
        if image:
            self.path_image = Path(image)
            try:
                copyfile(self.path_image, self.path_image_tmp)
                self.image_pixmap = QPixmap(str(self.path_image_tmp))
                self.ui.lbl_image.setPixmap(
                    self.image_pixmap.scaled(
                        self.ui.lbl_image.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    " ",
                    f"No se pudo abrir el archivo:\n{e}",
                )

    def check_inspection_hours(self):
        self.ui.sbx_inspection_hours.setVisible(
            True if self.ui.chb_inspection_hours.isChecked() else False
        )

    def check_inspection_km(self):
        self.ui.sbx_inspection_km.setVisible(
            True if self.ui.chb_inspection_km.isChecked() else False
        )

    def check_itv_expery(self):
        self.ui.date_itv_expiry.setVisible(
            True if self.ui.chb_itv_expiry.isChecked() else False
        )

    def check_tachograph_expery(self):
        self.ui.date_tachograph_expiry.setVisible(
            True if self.ui.chb_tachograph_expiry.isChecked() else False
        )

    def closeEvent(self, event):
        if self.is_adding:
            self.discard_changes(event)
        if self.is_editing:
            QMessageBox.warning(
                self,
                " ",
                "No puedes cerrar la ventana con la ficha del vehículo abierta. Debes cancelar o guardar los datos.",
            )
            event.ignore()

    def collect_vehicle_data(self):
        date_tachograph_expiry = (
            None
            if not self.ui.chb_tachograph_expiry.isChecked()
            else date(
                self.ui.date_tachograph_expiry.date().year(),
                self.ui.date_tachograph_expiry.date().month(),
                self.ui.date_tachograph_expiry.date().day(),
            )
        )
        date_itv_expiry = (
            None
            if not self.ui.chb_itv_expiry.isChecked()
            else date(
                self.ui.date_itv_expiry.date().year(),
                self.ui.date_itv_expiry.date().month(),
                self.ui.date_itv_expiry.date().day(),
            )
        )
        inspection_km = (
            None
            if not self.ui.chb_inspection_km.isChecked()
            else self.ui.sbx_inspection_km.value()
        )
        inspection_hours = (
            None
            if not self.ui.chb_inspection_hours.isChecked()
            else self.ui.sbx_inspection_hours.value()
        )
        return {
            "id": self.id if self.id else None,
            "alias": self.ui.txt_alias.text(),
            "chassis_number": self.ui.txt_chassis_number.text(),
            "license_plate": self.ui.txt_license_plate.text(),
            "brand": self.ui.txt_brand.text(),
            "model": self.ui.txt_model.text(),
            "tachograph_expiry": (
                date_tachograph_expiry.strftime("%Y-%m-%d")
                if date_tachograph_expiry
                else None
            ),
            "itv_expiry": (
                date_itv_expiry.strftime("%Y-%m-%d") if date_itv_expiry else None
            ),
            "inspection_km": inspection_km,
            "inspection_hours": inspection_hours,
            "deactivate": self.ui.chb_deactivate.isChecked(),
            "company_id": self.company_id,
        }

    def configuration_based_on_inspections(self):
        self.model_inspections = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_inspections.setModel(self.model_inspections)
        self.model_inspections.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "KMS",
                "Horas",
                "Aceite\nMotor",
                "Aceite\nCambio",
                "Aceite\nDiferen.",
                "Aceite\nHidrául.",
                "Filtro\nAceite",
                "Filtro\nCombus.",
                "Filtro\nAire",
                "Filtro\nPolen",
                "Filtro\nHidrául.",
            ]
        )
        self.ui.tvw_inspections.setColumnHidden(0, True)
        # Set height and width of columns
        self.ui.tvw_inspections.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.ui.tvw_inspections.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.ui.tvw_inspections.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.ui.tvw_inspections.setColumnWidth(4, 75)
        self.ui.tvw_inspections.setColumnWidth(5, 75)
        self.ui.tvw_inspections.setColumnWidth(6, 75)
        self.ui.tvw_inspections.setColumnWidth(7, 75)
        self.ui.tvw_inspections.setColumnWidth(8, 75)
        self.ui.tvw_inspections.setColumnWidth(9, 75)
        self.ui.tvw_inspections.setColumnWidth(10, 75)
        self.ui.tvw_inspections.setColumnWidth(11, 75)
        self.ui.tvw_inspections.setColumnWidth(12, 75)

    def configuration_based_on_vehicle_documents(self):
        self.model_vehicle_documents = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_aditional_coduments.setModel(self.model_vehicle_documents)
        self.model_vehicle_documents.setHorizontalHeaderLabels(
            [
                "Nombre",
            ]
        )
        # Set height and width of columns
        self.ui.tvw_aditional_coduments.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

    def configuration_based_on_workorders(self):
        self.model_workorders = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_workorders.setModel(self.model_workorders)
        self.model_workorders.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "Realizado por",
                "Descripción",
            ]
        )
        self.ui.tvw_workorders.setColumnHidden(0, True)
        # Set height and width of columns
        self.ui.tvw_workorders.setColumnWidth(1, 100)
        self.ui.tvw_workorders.setColumnWidth(2, 200)
        self.ui.tvw_workorders.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )

    def configuration_tableviews(self):
        # Hide index of rows
        self.ui.tvw_inspections.verticalHeader().setVisible(False)
        self.ui.tvw_aditional_coduments.verticalHeader().setVisible(False)
        self.ui.tvw_workorders.verticalHeader().setVisible(False)
        # Sets the table to not be directly editable
        self.ui.tvw_inspections.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.ui.tvw_aditional_coduments.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )
        self.ui.tvw_workorders.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Sets that multiple lines can't be selected
        self.ui.tvw_inspections.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self.ui.tvw_aditional_coduments.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self.ui.tvw_workorders.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self.ui.tvw_inspections.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.ui.tvw_aditional_coduments.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.ui.tvw_workorders.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.ui.tvw_inspections.resizeColumnsToContents()
        self.ui.tvw_aditional_coduments.resizeColumnsToContents()
        self.ui.tvw_workorders.resizeColumnsToContents()
        self.ui.tvw_inspections.setAlternatingRowColors(True)
        self.ui.tvw_aditional_coduments.setAlternatingRowColors(True)
        self.ui.tvw_workorders.setAlternatingRowColors(True)

    def delete_inspection(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_inspection_id()
        if selected_id is not None:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres eliminar esta revisión?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.inspections_controller.delete_inspection(
                    self.auth_manager.token, selected_id
                )
                self.on_load_inspections()
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def delete_workorder(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_workorder_id()
        if selected_id is not None:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres eliminar esta orden de trabajo?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.workorders_controller.delete_workorder(
                    self.auth_manager.token, selected_id
                )
                self.on_load_workorders()
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def disable_form_fields(self):
        self.set_form_fields_state(False)

    def discard_changes(self, event=None):
        answer = QMessageBox.question(
            self,
            " ",
            "Seguro quieres cancelar los cambios?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            if self.path_image_tmp:
                if self.path_image_tmp.exists():
                    self.path_image_tmp.unlink()
                    self.ui.lbl_image.clear()
            if self.is_adding:
                self.is_adding = False
                self.close()
            if self.is_editing:
                self.disable_form_fields()
                self.on_load_vehicle()
                self.is_editing = False
                if event:
                    event.ignore()
        else:
            if event:
                event.ignore()

    def edit_inspection(self):
        self.auth_manager.is_token_expired(self)
        if self.auth_manager.has_permission("ERV"):
            selected_id = self.get_selected_inspection_id()
            if selected_id is not None:
                from views.forms import frm_inspection

                self.form = frm_inspection(
                    self, self.auth_manager, True, selected_id, self.id
                )
                self.form.data_update_inspections.connect(self.on_load_inspections)
                self.form.exec()
            else:
                QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def edit_workorder(self):
        self.auth_manager.is_token_expired(self)
        selected_id = self.get_selected_workorder_id()
        if selected_id is not None:
            from views.forms import frm_workorder

            self.form = frm_workorder(
                self, self.auth_manager, True, selected_id, self.id, self.company_id
            )
            self.form.data_update_workorder.connect(self.on_load_workorders)
            self.form.exec()
        else:
            QMessageBox.information(self, " ", "No se ha elegido ningún registro.")

    def enable_form_fields(self):
        self.set_form_fields_state(True)
        self.is_editing = True if self.edit else False

    def get_last_date_inspection(self):
        last_inspection = ""
        if self.last_inspection is not None:
            last_inspection = datetime.strptime(
                self.last_inspection.get("date"), "%Y-%m-%d"
            )
        return last_inspection

    def get_last_date_workorder(self):
        last_workorder = ""
        if self.last_workorder is not None:
            last_workorder = datetime.strptime(
                self.last_workorder.get("date"), "%Y-%m-%d"
            )
        return last_workorder

    def get_next_kms_inspection(self):
        inspection_kms = self.ui.sbx_inspection_km.value()
        next_inspection = (
            inspection_kms + self.last_inspection.get("kms")
            if self.last_inspection is not None
            else ""
        )
        return next_inspection

    def get_selected_inspection_id(self):
        selected_index = self.ui.tvw_inspections.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_inspections.model().index(row, column).data()
        else:
            return None

    def get_selected_workorder_id(self):
        selected_index = self.ui.tvw_workorders.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_workorders.model().index(row, column).data()
        else:
            return None

    def get_vehicle(self):
        self.vehicle = self.vehicles_controller.get_vehicle(
            self.auth_manager.token, self.id
        )
        if "error" in self.vehicle:
            raise Exception(self.vehicle.get("error"))
        self.last_inspection = self.inspections_controller.get_last_inspection(
            self.auth_manager.token, self.id
        )
        self.last_workorder = self.workorders_controller.get_last_workorder(
            self.auth_manager.token, self.id
        )

    def handle_error(self, error_message):
        self.loading_dialog.close()
        QMessageBox.warning(self, " ", error_message)
        self.setEnabled(True)
        self.data_update.emit()

    def load_add(self):
        self.is_adding = True
        self.ui.btn_save.setEnabled(True)
        self.ui.btn_save.clicked.connect(self.on_add_clicked)
        self.enable_form_fields()

    def load_edit(self):
        self.on_load_vehicle()
        self.ui.btn_save.clicked.connect(self.on_save_clicked)
        self.disable_form_fields()
        self.setWindowTitle(f"Vehículo {self.vehicle.get('alias')}")

    def on_add_clicked(self):
        if not self.ui.txt_alias.text():
            QMessageBox.warning(self, " ", "El campo 'Alias' no puede estar vacío!")
            return
        self.auth_manager.is_token_expired(self)
        answer = QMessageBox.question(
            self,
            " ",
            "Seguro quieres añadir el vehículo?",
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
        if not self.ui.txt_alias.text():
            QMessageBox.warning(self, " ", "El campo 'Alias' no puede estar vacío!")
            return
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
        self.loading_dialog.close()
        if self.edit:
            self.setEnabled(True)
            self.disable_form_fields()
            self.is_editing = False
        else:
            self.is_adding = False
            self.is_editing = False
            self.edit = True
            self.load_edit()

        self.data_update.emit()

    def load_inspections(self):
        for item in self.inspections:
            inspection_date = get_date_format(item.get("date"))
            row = [
                QStandardItem(str(item.get("id"))),
                QStandardItem(inspection_date),
                QStandardItem(
                    str(get_format_miles(item.get("kms"))) if item.get("kms") else ""
                ),
                QStandardItem(
                    str(get_format_miles(item.get("hours")))
                    if item.get("hours")
                    else ""
                ),
                QStandardItem("Si" if item.get("motor_oil") else "No"),
                QStandardItem("Si" if item.get("transmission_oil") else "No"),
                QStandardItem("Si" if item.get("diferential_oil") else "No"),
                QStandardItem("Si" if item.get("hydraulic_oil") else "No"),
                QStandardItem("Si" if item.get("oil_filter") else "No"),
                QStandardItem("Si" if item.get("fuel_filter") else "No"),
                QStandardItem("Si" if item.get("air_filter") else "No"),
                QStandardItem("Si" if item.get("poller_filter") else "No"),
                QStandardItem("Si" if item.get("hydraulic_filter") else "No"),
            ]
            for item in row:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_inspections.appendRow(row)

        next_inspection = self.get_next_kms_inspection()
        self.ui.txt_kms_next_inspection.setText(
            get_format_miles(next_inspection) if next_inspection != "" else ""
        )

        last_inspection = self.get_last_date_inspection()
        self.ui.txt_date_last_inspection.setText(
            last_inspection.strftime("%d/%m/%Y") if last_inspection != "" else ""
        )

        self.on_task_finished()

    def load_vehicle(self):
        self.company_id = self.vehicle.get("company_id")
        self.ui.txt_alias.setText(self.vehicle.get("alias"))
        self.ui.txt_chassis_number.setText(self.vehicle.get("chassis_number"))
        self.ui.txt_license_plate.setText(self.vehicle.get("license_plate"))
        self.ui.txt_brand.setText(self.vehicle.get("brand"))
        self.ui.txt_model.setText(self.vehicle.get("model"))
        if self.vehicle.get("tachograph_expiry"):
            expiry_date = datetime.strptime(
                self.vehicle.get("tachograph_expiry"), "%Y-%m-%d"
            )
            self.ui.chb_tachograph_expiry.setChecked(True)
            qdate = QDate(
                expiry_date.year,
                expiry_date.month,
                expiry_date.day,
            )
            self.ui.date_tachograph_expiry.setDate(qdate)
        else:
            self.ui.chb_tachograph_expiry.setChecked(False)
            self.ui.date_tachograph_expiry.setVisible(False)
        if self.vehicle.get("itv_expiry"):
            expiry_date = datetime.strptime(self.vehicle.get("itv_expiry"), "%Y-%m-%d")
            self.ui.chb_itv_expiry.setChecked(True)
            qdate = QDate(
                expiry_date.year,
                expiry_date.month,
                expiry_date.day,
            )
            self.ui.date_itv_expiry.setDate(qdate)
        else:
            self.ui.chb_itv_expiry.setChecked(False)
            self.ui.date_itv_expiry.setVisible(False)
        if self.vehicle.get("inspection_km"):
            self.ui.chb_inspection_km.setChecked(True)
            self.ui.sbx_inspection_km.setValue(self.vehicle.get("inspection_km"))
        else:
            self.ui.chb_inspection_km.setChecked(False)
            self.ui.sbx_inspection_km.setVisible(False)
        if self.vehicle.get("inspection_hours"):
            self.ui.chb_inspection_hours.setChecked(True)
            self.ui.sbx_inspection_hours.setValue(self.vehicle.get("inspection_hours"))
        else:
            self.ui.chb_inspection_hours.setChecked(False)
            self.ui.sbx_inspection_hours.setVisible(False)

        current_kms = get_kms_vehicle(self.vehicle.get("license_plate"))
        self.ui.txt_current_kms.setText(
            get_format_miles(current_kms)
            if current_kms is not None and current_kms != "0"
            else ""
        )

        next_inspection = self.get_next_kms_inspection()
        self.ui.txt_next_inspection.setText(
            get_format_miles(next_inspection) if next_inspection != "" else ""
        )
        last_inspection = self.get_last_date_inspection()
        self.ui.txt_last_date_inspection.setText(
            last_inspection.strftime("%d/%m/%Y") if last_inspection != "" else ""
        )
        last_workorder = self.get_last_date_workorder()
        self.ui.txt_last_workorder.setText(
            last_workorder.strftime("%d/%m/%Y") if last_workorder != "" else ""
        )
        self.ui.chb_deactivate.setChecked(
            True if self.vehicle.get("deactivate") else False
        )
        self.on_task_finished()

    def load_workorders(self):
        # Set first and last workorder
        self.ui.txt_first_date_workorder.setText(
            self.date_first_workorder.strftime("%d/%m/%Y")
            if self.first_workorder
            else ""
        )
        self.ui.txt_last_date_workorder.setText(
            self.date_last_workorder.strftime("%d/%m/%Y") if self.last_workorder else ""
        )
        self.ui.date_from.setDateRange(
            QDate(
                self.date_first_workorder.year,
                self.date_first_workorder.month,
                self.date_first_workorder.day,
            ),
            QDate(
                self.date_last_workorder.year,
                self.date_last_workorder.month,
                self.date_last_workorder.day,
            ),
        )
        self.ui.date_to.setDateRange(
            QDate(
                self.date_first_workorder.year,
                self.date_first_workorder.month,
                self.date_first_workorder.day,
            ),
            QDate(
                self.date_last_workorder.year,
                self.date_last_workorder.month,
                self.date_last_workorder.day,
            ),
        )
        self.ui.date_from.setDate(
            QDate(
                self.date_from_workorder.year,
                self.date_from_workorder.month,
                self.date_from_workorder.day,
            )
        )
        self.ui.date_to.setDate(
            QDate(
                self.date_last_workorder.year,
                self.date_last_workorder.month,
                self.date_last_workorder.day,
            )
        )
        if self.workorders is not None:
            for item in self.workorders:
                workorder_date = get_date_format(item.get("date"))

                id_item = QStandardItem(str(item.get("id")))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                date_item = QStandardItem(workorder_date)
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                realized_by_item = QStandardItem(item.get("realized_by"))
                realized_by_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                description_item = QStandardItem(item.get("description"))
                description_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self.model_workorders.appendRow(
                    [
                        id_item,
                        date_item,
                        realized_by_item,
                        description_item,
                    ]
                )
            for row in range(self.model_workorders.rowCount()):
                self.ui.tvw_workorders.resizeRowToContents(row)
        self.on_task_finished()

    def on_load_vehicle(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_vehicle)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_vehicle)
        self.hilo.start()

    def on_load_inspections(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_inspections)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_inspections)
        self.hilo.start()

    def on_load_vehicle_documents(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_vehicle_documents)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_vehicle_documents)
        self.hilo.start()

    def on_load_workorders(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_workorders)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_workorders)
        self.hilo.start()

    def on_load_filtered_workorders(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_filtered_workorders)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_workorders)
        self.hilo.start()

    def remove_filters(self):
        self.ui.date_from.setDate(self.date_first_workorder)
        self.ui.date_to.setDate(self.date_last_workorder)
        self.ui.txt_search.setText("")
        self.on_load_workorders()

    def save(self):
        vehicle = self.collect_vehicle_data()
        response = self.files_controller.upload_image(
            self.path_image_tmp, self.path_subfolder_image
        )
        if "error" in response:
            raise Exception(response.get("error"))
        self.path_image_tmp.unlink()
        response = self.vehicles_controller.update_vehicle(
            self.auth_manager.token, vehicle
        )
        if "error" in response:
            raise Exception(response.get("error"))

    def set_form_fields_state(self, enabled: bool):
        self.windowTitle = "Editar vehículo" if self.edit else "Añadir vehículo"
        self.ui.btn_edit.setText("Cancelar" if enabled else "Editar")
        self.ui.btn_save.setText("Guardar" if self.edit else "Añadir")
        self.ui.btn_save.clicked.disconnect()
        self.ui.btn_save.clicked.connect(
            self.on_save_clicked if self.edit else self.on_add_clicked
        )
        self.ui.btn_edit.disconnect()
        self.ui.btn_edit.clicked.connect(
            self.discard_changes if enabled else self.enable_form_fields
        )
        self.ui.btn_close.setEnabled(not enabled)
        self.ui.tab_file.tabBar().setTabEnabled(
            1,
            True if self.auth_manager.has_permission("VRV") and not enabled else False,
        )
        self.ui.tab_file.tabBar().setTabEnabled(
            2,
            True if self.auth_manager.has_permission("VMV") and not enabled else False,
        )
        self.ui.tab_file.tabBar().setTabEnabled(
            3,
            True if self.auth_manager.has_permission("VDV") and not enabled else False,
        )
        self.ui.btn_image.setEnabled(enabled)
        self.ui.btn_save.setEnabled(enabled)
        text_fields = [
            self.ui.txt_alias,
            self.ui.txt_chassis_number,
            self.ui.txt_license_plate,
            self.ui.txt_brand,
            self.ui.txt_model,
        ]
        for field in text_fields:
            field.setReadOnly(not enabled)

        checkboxes = [
            self.ui.chb_tachograph_expiry,
            self.ui.chb_itv_expiry,
            self.ui.chb_inspection_km,
            self.ui.chb_inspection_hours,
        ]
        for checkbox in checkboxes:
            checkbox.setEnabled(enabled)

        date_fields = [
            self.ui.date_tachograph_expiry,
            self.ui.date_itv_expiry,
        ]
        spin_boxes = [
            self.ui.sbx_inspection_km,
            self.ui.sbx_inspection_hours,
        ]
        for field in date_fields + spin_boxes:
            field.setReadOnly(not enabled)
            if self.is_adding:
                field.setVisible(False)

        self.ui.chb_deactivate.setEnabled(enabled)

    def get_inspections(self):
        self.inspections_controller = InspectionsController()
        self.model_inspections.removeRows(0, self.model_inspections.rowCount())
        self.inspections = self.inspections_controller.get_inspections(
            self.auth_manager.token, self.id
        )

    def get_vehicle_documents(self):
        self.vehicle_documents_controlles = VehicleDocumentsController()
        self.model_inspections.removeRows(0, self.model_inspections.rowCount())
        self.inspections = self.inspections_controller.get_inspections(
            self.auth_manager.token, self.id
        )

    def update_tab(self, index):
        if index == 0:
            self.on_load_vehicle()
        if index == 1:
            self.on_load_inspections()
        if index == 2:
            self.on_load_workorders()

    def get_filtered_workorders(self):
        # Empty the list of workorders
        self.workorders = None
        # Instantiate the controller
        self.workorders_controller = WorkOrdersController()
        # Remove all rows from the model
        self.model_workorders.removeRows(0, self.model_workorders.rowCount())
        # Get the first workorder
        self.first_workorder = self.workorders_controller.get_first_workorder(
            self.auth_manager.token, self.id
        )
        if self.first_workorder is not None:
            self.workorders = self.workorders_controller.get_workorders(
                self.auth_manager.token,
                self.id,
                date.strftime(self.date_from_workorder, "%Y-%m-%d"),
                date.strftime(self.date_to_workorder, "%Y-%m-%d"),
                self.ui.txt_search.text(),
            )

    def get_workorders(self):
        # Empty the list of workorders
        self.workorders = None
        # Instantiate the controller
        self.workorders_controller = WorkOrdersController()
        # Remove all rows from the model
        self.model_workorders.removeRows(0, self.model_workorders.rowCount())
        # Get the first workorder
        self.first_workorder = self.workorders_controller.get_first_workorder(
            self.auth_manager.token, self.id
        )
        # If the first workorder is not None, convert it to a datetime object
        if self.first_workorder is not None:
            self.date_first_workorder = datetime.strptime(
                self.first_workorder.get("date"), "%Y-%m-%d"
            ).date()
            self.date_from_workorder = self.date_first_workorder
        else:
            self.date_first_workorder = date.today()
            self.date_from_workorder = date.today()
        # Get the last workorder
        self.last_workorder = self.workorders_controller.get_last_workorder(
            self.auth_manager.token, self.id
        )
        # If the last workorder is not None, convert it to a datetime object
        if self.last_workorder is not None:
            self.date_last_workorder = datetime.strptime(
                self.last_workorder.get("date"), "%Y-%m-%d"
            ).date()
            self.date_to_workorder = self.date_last_workorder
        else:
            self.date_last_workorder = date.today()
            self.date_to_workorder = date.today()
        if self.first_workorder is not None:
            self.workorders = self.workorders_controller.get_workorders(
                self.auth_manager.token,
                self.id,
                date.strftime(self.date_from_workorder, "%Y-%m-%d"),
                date.strftime(self.date_to_workorder, "%Y-%m-%d"),
                self.ui.txt_search.text(),
            )

import shutil, sys, webbrowser
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
from lib.decorators import track_user_activity
from lib.exceptions import *
from lib.methods import *
from lib.task_thread import *
from pathlib import Path
from shutil import copyfile
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QDragEnterEvent
from PyQt6.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableView,
    QHeaderView,
    QFileDialog,
)
from views.forms_py import Ui_frm_vehicle


@track_user_activity
class frm_vehicle(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, auth_manager: AuthManager, edit, id, company_id):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        # Controllers variables
        self.files_controller = FilesController()
        self.inspections_controller = InspectionsController()
        self.vehicles_controller = VehiclesController()
        self.vehicle_documents_controlles = VehicleDocumentsController()
        self.workorders_controller = WorkOrdersController()

        # General variables
        self.frm_users = form
        self.edit = edit
        self.id = id
        self.company_id = company_id
        self.vehicle = None
        self.is_adding = False
        self.is_editing = False

        # Inspection variables
        self.inspections = None
        self.last_inspection = None

        # Workorders variables
        self.workorders = None
        self.first_workorder = None
        self.last_workorder = None
        self.date_first_workorder = None
        self.date_last_workorder = None
        self.date_from_workorder = None
        self.date_to_workorder = None

        # Documents variables
        self.basic_documents = None

        # Vehicle Image variables
        self.path_image = None
        self.path_tmp = Path(sys.argv[0]).resolve().parent / "tmp"
        self.path_subfolder_image = f"{self.company_id}/vehicles/{self.id}/photos/image"
        self.path_subfolder_basic_documents = (
            f"{self.company_id}/vehicles/{self.id}/documents/basic"
        )
        self.path_subfolder_aditional_documents = (
            f"{self.company_id}/vehicles/{self.id}/documents/aditional"
        )

        # Form construct
        self.ui = Ui_frm_vehicle()
        self.ui.setupUi(self)

        # Tableviews configuration
        self.configuration_tableviews()
        self.configuration_based_on_inspections()
        self.configuration_based_on_vehicle_documents()
        self.configuration_based_on_workorders()

        # Events for vehicle
        self.ui.btn_edit.clicked.connect(self.enable_form_fields)
        self.ui.btn_save.clicked.connect(self.on_save_clicked)
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.chb_tachograph_expiry.stateChanged.connect(self.check_tachograph_expery)
        self.ui.chb_itv_expiry.stateChanged.connect(self.check_itv_expery)
        self.ui.chb_inspection_km.stateChanged.connect(self.check_inspection_km)
        self.ui.chb_inspection_hours.stateChanged.connect(self.check_inspection_hours)
        self.ui.sbx_inspection_km.valueChanged.connect(self.get_next_kms_inspection)
        self.ui.sbx_inspection_hours.valueChanged.connect(self.get_next_kms_inspection)
        self.ui.lbl_dragdrop_image.setAcceptDrops(True)
        self.ui.lbl_dragdrop_image.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_image.dropEvent = self.dropEventImage
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
        # Registration certificate
        self.ui.lbl_dragdrop_registration_certificate.setAcceptDrops(True)
        self.ui.lbl_dragdrop_registration_certificate.dragEnterEvent = (
            self.dragEnterEvent
        )
        self.ui.lbl_dragdrop_registration_certificate.dropEvent = (
            self.dropEventDocument(self.ui.lbl_dragdrop_registration_certificate)
        )
        self.ui.btn_view_registration_certificate.clicked.connect(
            lambda: self.view_basic_document("PERMISO CIRCULACIÓN.pdf")
        )
        self.ui.btn_delete_registration_certificate.clicked.connect(
            lambda: self.delete_basic_document("PERMISO CIRCULACIÓN.pdf")
        )
        # Technical specifications
        self.ui.lbl_dragdrop_technical_specifications.setAcceptDrops(True)
        self.ui.lbl_dragdrop_technical_specifications.dragEnterEvent = (
            self.dragEnterEvent
        )
        self.ui.lbl_dragdrop_technical_specifications.dropEvent = (
            self.dropEventDocument(self.ui.lbl_dragdrop_technical_specifications)
        )
        self.ui.btn_view_technical_specifications.clicked.connect(
            lambda: self.view_basic_document("FICHA TÉCNICA.pdf")
        )
        self.ui.btn_delete_technical_specifications.clicked.connect(
            lambda: self.delete_basic_document("FICHA TÉCNICA.pdf")
        )
        # Tachograph inspection
        self.ui.lbl_dragdrop_tachograph_inspection.setAcceptDrops(True)
        self.ui.lbl_dragdrop_tachograph_inspection.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_tachograph_inspection.dropEvent = self.dropEventDocument(
            self.ui.lbl_dragdrop_tachograph_inspection
        )
        self.ui.btn_view_tachograph_inspection.clicked.connect(
            lambda: self.view_basic_document("REVISIÓN TACÓGRAFO.pdf")
        )
        self.ui.btn_delete_tachograph_inspection.clicked.connect(
            lambda: self.delete_basic_document("REVISIÓN TACÓGRAFO.pdf")
        )
        # Transport card
        self.ui.lbl_dragdrop_transport_card.setAcceptDrops(True)
        self.ui.lbl_dragdrop_transport_card.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_transport_card.dropEvent = self.dropEventDocument(
            self.ui.lbl_dragdrop_transport_card
        )
        self.ui.btn_view_transport_card.clicked.connect(
            lambda: self.view_basic_document("TARJETA TRANSPORTE.pdf")
        )
        self.ui.btn_delete_transport_card.clicked.connect(
            lambda: self.delete_basic_document("TARJETA TRANSPORTE.pdf")
        )
        # Green card
        self.ui.lbl_dragdrop_green_card.setAcceptDrops(True)
        self.ui.lbl_dragdrop_green_card.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_green_card.dropEvent = self.dropEventDocument(
            self.ui.lbl_dragdrop_green_card
        )
        self.ui.btn_view_green_card.clicked.connect(
            lambda: self.view_basic_document("CARTA VERDE.pdf")
        )
        self.ui.btn_delete_green_card.clicked.connect(
            lambda: self.delete_basic_document("CARTA VERDE.pdf")
        )
        # Insurance policy
        self.ui.lbl_dragdrop_insurance_policy.setAcceptDrops(True)
        self.ui.lbl_dragdrop_insurance_policy.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_insurance_policy.dropEvent = self.dropEventDocument(
            self.ui.lbl_dragdrop_insurance_policy
        )
        self.ui.btn_view_insurance_policy.clicked.connect(
            lambda: self.view_basic_document("PÓLIZA SEGURO.pdf")
        )
        self.ui.btn_delete_insurance_policy.clicked.connect(
            lambda: self.delete_basic_document("PÓLIZA SEGURO.pdf")
        )
        # Insurance receipt
        self.ui.lbl_dragdrop_insurance_receipt.setAcceptDrops(True)
        self.ui.lbl_dragdrop_insurance_receipt.dragEnterEvent = self.dragEnterEvent
        self.ui.lbl_dragdrop_insurance_receipt.dropEvent = self.dropEventDocument(
            self.ui.lbl_dragdrop_insurance_receipt
        )
        self.ui.btn_view_insurance_receipt.clicked.connect(
            lambda: self.view_basic_document("RECIBO SEGURO.pdf")
        )
        self.ui.btn_delete_insurance_receipt.clicked.connect(
            lambda: self.delete_basic_document("RECIBO SEGURO.pdf")
        )

        # Event aditional documents
        self.ui.btn_view_aditional_document.clicked.connect(
            lambda: self.view_aditional_document(
                self.get_selected_aditional_document_id()
            )
        )
        self.ui.tvw_aditional_coduments.doubleClicked.connect(
            lambda: self.view_aditional_document(
                self.get_selected_aditional_document_id()
            )
        )
        self.ui.btn_add_aditional_document.clicked.connect(self.add_aditional_document)
        self.ui.btn_edit_aditional_document.clicked.connect(
            self.edit_aditional_document
        )
        self.ui.btn_delete_aditional_document.clicked.connect(
            self.delete_aditional_document
        )

        # Check permissions
        # Vehicle permissions
        self.ui.btn_edit.setEnabled(self.auth_manager.has_permission("EV"))
        # Inspection permissions
        self.ui.btn_add_inspection.setEnabled(self.auth_manager.has_permission("ARV"))
        self.ui.btn_edit_inspection.setEnabled(self.auth_manager.has_permission("ERV"))
        self.ui.btn_delete_inspection.setEnabled(
            self.auth_manager.has_permission("DRV")
        )
        # Workorders permissions
        self.ui.btn_add_workorder.setEnabled(self.auth_manager.has_permission("AMV"))
        if not self.auth_manager.has_permission("EMV"):
            self.ui.btn_edit_workorder.setText("Ver")
            if not self.auth_manager.has_permission("VMV"):
                self.ui.btn_edit_workorder.setEnabled(False)
        self.ui.btn_delete_workorder.setEnabled(self.auth_manager.has_permission("DMV"))
        # Documents permissions
        # Basic documents
        self.ui.btn_delete_registration_certificate.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_technical_specifications.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_tachograph_inspection.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_transport_card.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_green_card.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_insurance_policy.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.btn_delete_insurance_receipt.setEnabled(
            self.auth_manager.has_permission("DDV")
        )
        self.ui.lbl_dragdrop_registration_certificate.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_technical_specifications.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_tachograph_inspection.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_transport_card.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_green_card.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_insurance_policy.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.lbl_dragdrop_insurance_receipt.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        # Aditional documents
        self.ui.btn_add_aditional_document.setEnabled(
            self.auth_manager.has_permission("ADV")
        )
        self.ui.btn_edit_aditional_document.setEnabled(
            self.auth_manager.has_permission("EDV")
        )
        self.ui.btn_delete_aditional_document.setEnabled(
            self.auth_manager.has_permission("DDV")
        )

        # Load form addition or edition
        if edit:
            self.load_edit()
        else:
            self.load_add()

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

    def add_aditional_document(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_aditional_document

        self.form = frm_aditional_document(
            self, self.auth_manager, False, self.id, self.company_id, None
        )
        self.form.data_update_documents.connect(self.on_load_documents)
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
        delete_temporary_folder()
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
        self.model_aditional_documents = QStandardItemModel()
        # Add model on table view
        self.ui.tvw_aditional_coduments.setModel(self.model_aditional_documents)
        self.model_aditional_documents.setHorizontalHeaderLabels(
            [
                "Documentos",
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

    def copy_file(self, path_image: str):
        self.auth_manager.is_token_expired(self)
        self.path_image = Path(path_image)
        try:
            path_tmp_image = self.path_tmp / self.path_image.name
            copyfile(self.path_image, path_tmp_image)
            self.set_image(path_tmp_image, None)
        except Exception as e:
            QMessageBox.critical(
                self,
                " ",
                f"No se pudo abrir el archivo:\n{e}",
            )

    def delete_aditional_document(self):
        document = self.get_selected_aditional_document_id()
        if document:
            answer = QMessageBox.question(
                self,
                "Eliminar documento",
                f"Seguro quieres eliminar el documento '{document}'?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                response = self.files_controller.delete_file(
                    self.auth_manager.token,
                    self.path_subfolder_aditional_documents,
                    document,
                )
                if "error" in response:
                    QMessageBox.information(
                        self,
                        "Eliminar documento",
                        f"No se puede eliminar el documento: {response.get('error')}",
                    )
                    return
                self.load_documents()

    def delete_basic_document(self, document: str):
        answer = QMessageBox.question(
            self,
            "Eliminar documento",
            f"Seguro quieres eliminar el documento '{document}'?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            response = self.files_controller.delete_file(
                self.auth_manager.token, self.path_subfolder_basic_documents, document
            )
            if "error" in response:
                QMessageBox.information(
                    self,
                    "Eliminar documento",
                    f"No se puede eliminar el documento: {response.get('error')}",
                )
                return
            self.load_documents()

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
            delete_temporary_folder()
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEventImage(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = Path(urls[0].toLocalFile())
            if file_path.is_file():
                if (
                    str(file_path).endswith(".png")
                    or str(file_path).endswith(".PNG")
                    or str(file_path).endswith(".jpg")
                    or str(file_path).endswith(".JPG")
                    or str(file_path).endswith(".jpeg")
                    or str(file_path).endswith(".JPEG")
                ):
                    try:
                        self.copy_file(file_path)
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
                        "El archivo no es una imagen válido.\n"
                        "Por favor, sube un archivo de imagen.",
                    )

    def dropEventDocument(self, label: QLabel):
        def handler(event: QDragEnterEvent):
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

            label_to_filename = {
                "lbl_dragdrop_registration_certificate": "PERMISO CIRCULACIÓN.pdf",
                "lbl_dragdrop_technical_specifications": "FICHA TÉCNICA.pdf",
                "lbl_dragdrop_tachograph_inspection": "REVISIÓN TACÓGRAFO.pdf",
                "lbl_dragdrop_transport_card": "TARJETA TRANSPORTE.pdf",
                "lbl_dragdrop_green_card": "CARTA VERDE.pdf",
                "lbl_dragdrop_insurance_policy": "PÓLIZA SEGURO.pdf",
                "lbl_dragdrop_insurance_receipt": "RECIBO SEGURO.pdf",
            }

            filename = label_to_filename.get(label.objectName())
            if not filename:
                return

            try:
                self.files_controller.upload_or_replace_file(
                    self.auth_manager.token,
                    file_path,
                    self.path_subfolder_basic_documents,
                    filename,
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"No se pudo subir el archivo:\n{e}"
                )
            finally:
                self.load_documents()

        return handler

    def edit_aditional_document(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_aditional_document

        document = self.get_selected_aditional_document_id()
        if document:
            self.form = frm_aditional_document(
                self, self.auth_manager, True, self.id, self.company_id, document
            )
            self.form.data_update_documents.connect(self.on_load_documents)
            self.form.exec()

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

    def get_documents(self):
        self.model_aditional_documents.removeRows(
            0, self.model_aditional_documents.rowCount()
        )
        self.basic_documents = self.files_controller.get_files(
            self.auth_manager.token, self.path_subfolder_basic_documents
        )

    def get_inspections(self):
        self.inspections_controller = InspectionsController()
        self.model_inspections.removeRows(0, self.model_inspections.rowCount())
        self.inspections = self.inspections_controller.get_inspections(
            self.auth_manager.token, self.id
        )

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

    def get_selected_aditional_document_id(self):
        selected_index = (
            self.ui.tvw_aditional_coduments.selectionModel().selectedIndexes()
        )
        if selected_index:
            row = selected_index[0].row()
            column = selected_index[0].column()
            return self.ui.tvw_aditional_coduments.model().index(row, column).data()
        else:
            return None

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
        response = self.files_controller.get_files(
            self.auth_manager.token,
            self.path_subfolder_image,
        )
        if "error" in response:
            raise Exception(response.get("error"))
        if response:
            response = self.files_controller.get_file(
                self.auth_manager.token,
                self.path_subfolder_image,
                response[0],
            )
            try:
                self.set_image(None, response)
            except Exception as e:
                print(f"No se pudo abrir el archivo:\n{e}")

        self.last_inspection = self.inspections_controller.get_last_inspection(
            self.auth_manager.token, self.id
        )
        self.last_workorder = self.workorders_controller.get_last_workorder(
            self.auth_manager.token, self.id
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

    def handle_error(self, error_message, error_details):
        self.loading_dialog.close()
        show_error_dialog(self, error_message, error_details)
        self.setEnabled(True)
        self.data_update.emit()

    def load_add(self):
        self.is_adding = True
        self.ui.btn_save.setEnabled(True)
        self.enable_form_fields()

    def load_documents(self):
        self.get_documents()
        # Load registration_certificate
        registration_certificate = "PERMISO CIRCULACIÓN.pdf" in self.basic_documents
        self.ui.lbl_registration_certificate.setText(
            "Permiso Circulación ✔"
            if registration_certificate
            else "Permiso Circulación ✘"
        )
        self.ui.btn_view_registration_certificate.setEnabled(registration_certificate)
        # Load technical specifications
        technical_specifications = "FICHA TÉCNICA.pdf" in self.basic_documents
        self.ui.lbl_technical_specifications.setText(
            "Ficha Técnica ✔" if technical_specifications else "Ficha Técnica ✘"
        )
        self.ui.btn_view_technical_specifications.setEnabled(technical_specifications)

        # Load tachograph inspection
        tachograph_inspection = "REVISIÓN TACÓGRAFO.pdf" in self.basic_documents
        self.ui.lbl_tachograph_inspection.setText(
            "Revisión Tacógrafo ✔" if tachograph_inspection else "Revisión Tacógrafo ✘"
        )
        self.ui.btn_view_tachograph_inspection.setEnabled(tachograph_inspection)
        # Load transport card
        transport_card = "TARJETA TRANSPORTE.pdf" in self.basic_documents
        self.ui.lbl_transport_card.setText(
            "Tarjeta Transporte ✔" if transport_card else "Tarjeta Transporte ✘"
        )
        self.ui.btn_view_transport_card.setEnabled(transport_card)
        # Load green card
        green_card = "CARTA VERDE.pdf" in self.basic_documents
        self.ui.lbl_green_card.setText(
            "Carta Verde ✔" if green_card else "Carta Verde ✘"
        )
        self.ui.btn_view_green_card.setEnabled(green_card)
        # Load insurance policy
        insurance_policy = "PÓLIZA SEGURO.pdf" in self.basic_documents
        self.ui.lbl_insurance_policy.setText(
            "Póliza Seguro ✔" if insurance_policy else "Póliza Seguro ✘"
        )
        self.ui.btn_view_insurance_policy.setEnabled(insurance_policy)
        # Load insuracne receipt
        insurance_receipt = "RECIBO SEGURO.pdf" in self.basic_documents
        self.ui.lbl_insurance_receipt.setText(
            "Recibo Seguro ✔" if insurance_receipt else "Recibo Seguro ✘"
        )
        self.ui.btn_view_insurance_receipt.setEnabled(insurance_receipt)

        # Load aditional documents
        response = self.files_controller.get_files(
            self.auth_manager.token, self.path_subfolder_aditional_documents
        )
        for document in response:
            row = [QStandardItem(document)]
            self.model_aditional_documents.appendRow(row)
        if self.auth_manager.has_permission("ADV"):
            self.ui.btn_add_aditional_document.setEnabled(True)
        if self.auth_manager.has_permission("EDV"):
            self.ui.lbl_dragdrop_registration_certificate.setEnabled(True)
            self.ui.lbl_dragdrop_technical_specifications.setEnabled(True)
            self.ui.lbl_dragdrop_tachograph_inspection.setEnabled(True)
            self.ui.lbl_dragdrop_transport_card.setEnabled(True)
            self.ui.lbl_dragdrop_green_card.setEnabled(True)
            self.ui.lbl_dragdrop_insurance_policy.setEnabled(True)
            self.ui.lbl_dragdrop_insurance_receipt.setEnabled(True)
            self.ui.btn_edit_aditional_document.setEnabled(True)
        if self.auth_manager.has_permission("DDV"):
            self.ui.btn_delete_registration_certificate.setEnabled(
                registration_certificate
            )
            self.ui.btn_delete_technical_specifications.setEnabled(
                technical_specifications
            )
            self.ui.btn_delete_tachograph_inspection.setEnabled(tachograph_inspection)
            self.ui.btn_delete_transport_card.setEnabled(transport_card)
            self.ui.btn_delete_green_card.setEnabled(green_card)
            self.ui.btn_delete_insurance_policy.setEnabled(insurance_policy)
            self.ui.btn_delete_insurance_receipt.setEnabled(insurance_receipt)
            self.ui.btn_delete_aditional_document.setEnabled(True)
        self.on_task_finished()

    def load_edit(self):
        self.on_load_vehicle()
        self.disable_form_fields()

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
        self.setWindowTitle(f"Vehículo {self.vehicle.get('alias')}")
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
        self.is_adding = False
        self.edit = True
        self.is_editing = False
        self.on_task_finished()
        self.disable_form_fields()

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

    def on_load_documents(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_documents)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_documents)
        self.hilo.start()

    def on_load_filtered_workorders(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_filtered_workorders)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_workorders)
        self.hilo.start()

    def on_load_inspections(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_inspections)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_inspections)
        self.hilo.start()

    def on_load_vehicle(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_vehicle)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_vehicle)
        self.hilo.start()

    def on_load_workorders(self):
        self.setEnabled(False)
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        self.hilo = TaskThread(self.get_workorders)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.load_workorders)
        self.hilo.start()

    def on_save_clicked(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_alias.text():
            QMessageBox.warning(self, " ", "El campo 'Alias' no puede estar vacío!")
            return
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
        else:
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
            self.hilo = TaskThread(self.save)
            self.hilo.error.connect(self.handle_error)
            self.hilo.finished.connect(self.load_vehicle)
            self.hilo.start()

    def on_task_finished(self):
        self.loading_dialog.close()
        self.setEnabled(True)
        self.data_update.emit()

    def remove_filters(self):
        self.ui.date_from.setDate(self.date_first_workorder)
        self.ui.date_to.setDate(self.date_last_workorder)
        self.ui.txt_search.setText("")
        self.on_load_workorders()

    def save(self):
        vehicle = self.collect_vehicle_data()
        if self.edit:
            response = self.vehicles_controller.update_vehicle(
                self.auth_manager.token, vehicle
            )
        else:
            response = self.vehicles_controller.add_vehicle(
                self.auth_manager.token, vehicle
            )
        if "error" in response:
            raise Exception(response.get("error"))
        self.vehicle = response.get("vehicle")
        self.id = self.vehicle.get("id")
        self.path_subfolder_image = f"{self.company_id}/vehicles/{self.id}/photos/image"
        if self.path_tmp.exists() and any(self.path_tmp.iterdir()):
            path_tmp_image = self.path_tmp / self.path_image.name
            file_name = None
            if path_tmp_image.name.endswith(".png"):
                file_name = f"{self.id}.png"
            elif path_tmp_image.name.endswith(".PNG"):
                file_name = f"{self.id}.PNG"
            elif path_tmp_image.name.endswith(".jpg"):
                file_name = f"{self.id}.jpg"
            elif path_tmp_image.name.endswith(".JPG"):
                file_name = f"{self.id}.JPG"
            elif path_tmp_image.name.endswith(".jpeg"):
                file_name = f"{self.id}.jpeg"
            elif path_tmp_image.name.endswith(".JPEG"):
                file_name = f"{self.id}.JPEG"
            if any(self.path_tmp.iterdir()):
                response = self.files_controller.upload_or_replace_file(
                    self.auth_manager.token,
                    path_tmp_image,
                    self.path_subfolder_image,
                    file_name,
                )
                if "error" in response:
                    raise Exception(response.get("error"))

    def set_form_fields_state(self, enabled: bool):
        self.windowTitle = "Editar vehículo" if self.edit else "Añadir vehículo"
        self.ui.btn_edit.setText("Cancelar" if enabled else "Editar")
        self.ui.btn_save.setText("Guardar" if self.edit else "Añadir")
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
        self.ui.lbl_dragdrop_image.setEnabled(enabled)
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

    def set_image(self, path_image, image):
        if path_image:
            self.image_pixmap = QPixmap(str(path_image))
            self.ui.lbl_image.setPixmap(
                self.image_pixmap.scaled(
                    self.ui.lbl_image.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        if image:
            self.image_pixmap = QPixmap()
            self.image_pixmap.loadFromData(image)
            self.ui.lbl_image.setPixmap(
                self.image_pixmap.scaled(
                    self.ui.lbl_image.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def update_tab(self, index):
        self.auth_manager.is_token_expired(self)
        if index == 0:
            self.on_load_vehicle()
        if index == 1:
            self.on_load_inspections()
        if index == 2:
            self.on_load_workorders()
        if index == 3:
            self.on_load_documents()

    def view_aditional_document(self, document):
        self.auth_manager.is_token_expired(self)
        if document:
            response = self.files_controller.get_file(
                self.auth_manager.token,
                self.path_subfolder_aditional_documents,
                document,
            )
            try:
                file_path = Path(sys.argv[0]).resolve().parent / "tmp" / document
                with open(file_path, "wb") as f:
                    f.write(response)
                webbrowser.open(str(file_path))
            except Exception as e:
                QMessageBox.critical(
                    self,
                    " ",
                    f"No se pudo abrir el archivo:\n{e}",
                )

    def view_basic_document(self, document):
        self.auth_manager.is_token_expired(self)
        response = self.files_controller.get_file(
            self.auth_manager.token,
            self.path_subfolder_basic_documents,
            document,
        )
        try:
            file_path = Path(sys.argv[0]).resolve().parent / "tmp" / document
            with open(file_path, "wb") as f:
                f.write(response)
            webbrowser.open(str(file_path))
        except Exception as e:
            QMessageBox.critical(
                self,
                " ",
                f"No se pudo abrir el archivo:\n{e}",
            )

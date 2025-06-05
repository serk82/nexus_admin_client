from controllers import (
    CompaniesController,
    UsersController,
    VehiclesController,
    InspectionsController,
)
from controllers import AuthManager
from datetime import datetime, timedelta
from lib.methods import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtWidgets import (
    QDialog,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from views.forms_py import Ui_frm_notifications


class frm_notifications(QDialog):

    def __init__(self, auth_manager: AuthManager):
        super().__init__()
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        # Variables
        self.companies_controller = CompaniesController()
        self.inspections_controller = InspectionsController()
        self.users_controller = UsersController()
        self.vehicles_controller = VehiclesController()
        self.today = datetime.now().date()
        self.all_current_kms = get_kms_vehicles()

        self.user = self.users_controller.get_user_by_id(
            self.auth_manager.token, self.auth_manager.user_id
        )
        self.user_notification_itv_expiry = self.user.get("notification_itv_expiry")
        self.user_notification_inspection_kms_expiry = self.user.get(
            "notification_inspection_kms_expiry"
        )
        if self.auth_manager.has_permission("CT"):
            self.companies = self.companies_controller.get_companies(
                self.auth_manager.token
            )
        else:
            self.companies = self.users_controller.get_companies_from_user(
                self.auth_manager.token, self.auth_manager.user_id
            )
        self.notifications = []

        self.ui = Ui_frm_notifications()
        self.ui.setupUi(self)

        self.setFixedWidth(700)

        # Events
        self.ui.btn_close.clicked.connect(self.close)

        # Create model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Notificación", "Aviso"])

        # Load notifications
        self.load_notifications()

        # Sets that multiple lines can't be selected
        self.ui.tvw_notifications.setModel(self.model)
        self.ui.tvw_notifications.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.ui.tvw_notifications.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.tvw_notifications.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.ui.tvw_notifications.setColumnWidth(0, 300)
        self.ui.tvw_notifications.setColumnWidth(1, 300)
        self.ui.tvw_notifications.expandAll()

    def load_notifications(self):
        for company in self.companies:
            company_item = QStandardItem(str(company.get("name")))
            vehicle_items = self.check_vehicle(company)
            if vehicle_items:
                for vehicle_item in vehicle_items:
                    company_item.appendRow([vehicle_item])
                self.model.appendRow([company_item, QStandardItem("")])

    def check_vehicle(self, company):
        vehicles = self.vehicles_controller.get_vehicles(
            self.auth_manager.token, company.get("id")
        )
        vehicle_items = []
        for vehicle in vehicles:
            vehicle_item = QStandardItem(vehicle.get("alias"))
            itv_item = self.check_itv(vehicle)
            if itv_item:
                vehicle_item.appendRow(itv_item)
            inspection_kms_item = self.check_inspection(vehicle)
            if inspection_kms_item:
                vehicle_item.appendRow(inspection_kms_item)
            if vehicle_item.rowCount() > 0:
                vehicle_items.append(vehicle_item)
        return vehicle_items

    def check_itv(self, vehicle):
        if not vehicle.get("deactivate"):
            if (
                self.user_notification_itv_expiry is not None
                and vehicle.get("itv_expiry") is not None
            ):
                target_date = datetime.strptime(vehicle.get("itv_expiry"), "%Y-%m-%d")
                limit_date = target_date.date() - timedelta(
                    days=self.user_notification_itv_expiry
                )
                if self.today >= limit_date:
                    days_remainig = target_date.date() - self.today
                    itv_expiry_item = QStandardItem(
                        f"Caducidad ITV: {target_date.date().strftime('%d/%m/%Y')}"
                    )
                    days_remainig_item = QStandardItem()
                    if days_remainig.days < 0:
                        days_remainig_item.setForeground(QColor("red"))
                        days_remainig_item.setText(
                            f"!!! ITV Caducada !!! han pasado {days_remainig.days} días"
                        )
                    elif days_remainig.days < 10 and days_remainig.days >= 0:
                        days_remainig_item.setForeground(QColor("orange"))
                        days_remainig_item.setText(
                            f"ITV a punto de caducar. Quedan {days_remainig.days} días"
                        )
                    else:
                        days_remainig_item.setForeground(QColor("green"))
                        days_remainig_item.setText(f"Quedan {days_remainig.days} días")
                    return [
                        itv_expiry_item,
                        days_remainig_item,
                    ]
        return None

    def check_inspection(self, vehicle):
        if not vehicle.get("deactivate"):
            if (
                self.user_notification_inspection_kms_expiry is not None
                and vehicle.get("inspection_km") is not None
            ):
                current_kms = None
                for current_kms_vehicle in self.all_current_kms.findall("GRUA"):
                    if current_kms_vehicle.find("MATRICULA").text == vehicle.get("license_plate"):
                        current_kms = current_kms_vehicle.find("KMS").text
                        break
                next_inspection = self.get_next_kms_inspection(
                    vehicle.get("id"), vehicle.get("inspection_km")
                )
                if current_kms and next_inspection:
                    current_kms = int(current_kms)
                    kms_remainig = next_inspection - current_kms
                    if kms_remainig <= self.user_notification_inspection_kms_expiry:
                        inspection_kms_item = QStandardItem(
                            f"Revisión a los {get_format_miles(next_inspection)} KMS"
                        )
                        kms_remainig_item = QStandardItem()
                        if kms_remainig < 0:
                            kms_remainig_item.setForeground(QColor("red"))
                            kms_remainig_item.setText(
                                f"!!! Revisión Caducada !!! han pasado {get_format_miles(-kms_remainig)} KMS"
                            )
                        elif kms_remainig < 100 and kms_remainig >= 0:
                            kms_remainig_item.setForeground(QColor("orange"))
                            kms_remainig_item.setText(
                                f"Revisión a punto de caducar. Quedan {get_format_miles(kms_remainig)} KMS"
                            )
                        else:
                            kms_remainig_item.setForeground(QColor("green"))
                            kms_remainig_item.setText(
                                f"Quedan {get_format_miles(kms_remainig)} KMS"
                            )
                        return [
                            inspection_kms_item,
                            kms_remainig_item,
                        ]
        return None

    def get_next_kms_inspection(self, vehicle_id, target_kms):
        last_inspection = self.inspections_controller.get_last_inspection(
            self.auth_manager.token, vehicle_id
        )
        next_inspection = (
            target_kms + last_inspection.get("kms")
            if last_inspection is not None
            else None
        )
        return next_inspection

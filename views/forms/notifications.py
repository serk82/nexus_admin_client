from controllers import CompaniesController, UsersController, VehiclesController
from controllers import AuthManager
from datetime import datetime, timedelta
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
        self.users_controller = UsersController()
        self.vehicles_controller = VehiclesController()
        self.notity_company = None
        self.today = datetime.now().date()

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

        self.setFixedWidth(650)

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
        # self.ui.tvw_notifications.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.ui.tvw_notifications.expandAll()

    def load_notifications(self):
        for company in self.companies:
            self.notify_company = False
            company_item = QStandardItem(str(company.get("name")))
            vehicle_items = self.check_itv(company)
            for vehicle_item in vehicle_items:
                company_item.appendRow([vehicle_item])
            if self.notify_company:
                self.model.appendRow([company_item, QStandardItem("")])

    def check_itv(self, company):
        vehicles = self.vehicles_controller.get_vehicles(
            self.auth_manager.token, company.get("id")
        )
        vehicle_items = []
        for vehicle in vehicles:
            notify_vehicle = False
            notify_itv_expiry = False
            if not vehicle.get('deactivate'):
                if (
                    self.user_notification_itv_expiry is not None
                    and vehicle.get("itv_expiry") is not None
                ):
                    target_date = datetime.strptime(vehicle.get("itv_expiry"), "%Y-%m-%d")
                    limit_date = target_date.date() - timedelta(
                        days=self.user_notification_itv_expiry
                    )
                    if self.today >= limit_date:
                        notify_vehicle = True
                        notify_itv_expiry = True
                        days_remainig = target_date.date() - self.today
                if notify_vehicle:
                    self.notify_company = True
                    vehicle_item = QStandardItem(vehicle.get("alias"))
                    if notify_itv_expiry:
                        itv_expiry_item = QStandardItem(
                            f"Caducidad ITV: {target_date.date()}"
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
                    vehicle_item.appendRow(
                        [
                            itv_expiry_item,
                            days_remainig_item,
                        ]
                    )
                    vehicle_items.append(vehicle_item)
        return vehicle_items

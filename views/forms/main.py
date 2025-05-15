from controllers import AuthManager, CompaniesController
from lib.methods import *
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from views.forms_py import Ui_frm_main
from views.forms.vehicles import frm_vehicles


class frm_main(QMainWindow):

    def __init__(self, auth_manager: AuthManager, company_id):
        super().__init__()
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        self.companies_controller = CompaniesController()

        self.company = self.companies_controller.get_company(
            self.auth_manager.token, company_id
        )

        # Load UI
        self.ui = Ui_frm_main()
        self.ui.setupUi(self)

        self.setWindowTitle("Nexus Admin - " + self.company.get("name"))

        # Events
        self.ui.action_change_company.triggered.connect(self.options)
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_close_session.triggered.connect(self.close_session)
        self.ui.action_vehicles.triggered.connect(self.vehicles)

        # Check permissions
        self.ui.action_vehicles.setEnabled(self.auth_manager.has_permission("VV"))

    def options(self):
        self.auth_manager.is_token_expired(self)
        from views.forms.options import frm_options

        self.form = frm_options(self.auth_manager)
        self.form.show()
        self.close()

    def vehicles(self):
        self.auth_manager.is_token_expired(self)
        self.form = frm_vehicles(self, self.auth_manager, self.company.get("id"))
        self.form.exec()

    def close_session(self):
        from .login import frm_login

        self.form = frm_login()
        self.form.show()
        self.close()

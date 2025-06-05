import sys
import subprocess
from controllers import AuthManager
from lib.methods import *
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from views.forms_py import Ui_frm_configuration
from .table_view import frm_table_view


class frm_configuration(QMainWindow):

    def __init__(self, auth_manager: AuthManager):
        super().__init__()
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        self.is_logged_out = False

        # Load UI
        self.ui = Ui_frm_configuration()
        self.ui.setupUi(self)

        self.setWindowTitle("Nexus Admin - CONFIGURACIÓN")

        # Events
        self.ui.action_Copia_de_seguridad.triggered.connect(self.backup)
        self.ui.action_change_company.triggered.connect(self.options)
        self.ui.action_close_session.triggered.connect(self.close_session)
        self.ui.action_companies.triggered.connect(self.companies)
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_permissions.triggered.connect(self.permissions)
        self.ui.action_roles.triggered.connect(self.roles)
        self.ui.action_users.triggered.connect(self.users)
        self.ui.action_notifications.triggered.connect(self.notification_settings)

        self.load_configuration()

    def backup(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_backup

        self.form = frm_backup(self, self.auth_manager)
        self.form.exec()

    def close_session(self):
        from .login import frm_login

        self.form = frm_login()
        self.form.show()
        self.close()

    def companies(self):
        self.auth_manager.is_token_expired(self)
        self.form = frm_table_view(self, self.auth_manager, "companies")
        self.form.exec()

    def load_configuration(self):
        if not self.auth_manager.has_permission("CT"):
            self.ui.action_companies.setVisible(False)
            self.ui.action_permissions.setVisible(False)
            self.ui.action_roles.setVisible(False)
            self.ui.action_users.setVisible(False)
            self.ui.action_Copia_de_seguridad.setVisible(False)
            self.ui.menubar.removeAction(self.ui.menu_Seguridad.menuAction())

    def notification_settings(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_notification_settings

        self.form = frm_notification_settings(
            self, self.auth_manager, self.auth_manager.user_id
        )
        self.form.exec()

    def permissions(self):
        self.auth_manager.is_token_expired(self)
        from views.forms import frm_permissions

        self.form = frm_permissions(self, self.auth_manager)
        self.form.exec()

    def options(self):
        from views.forms.options import frm_options

        self.form = frm_options(self.auth_manager)
        self.form.show()
        self.is_logged_out = True
        self.close()

    def roles(self):
        self.auth_manager.is_token_expired(self)
        self.form = frm_table_view(self, self.auth_manager, "roles")
        self.form.exec()

    def users(self):
        self.auth_manager.is_token_expired(self)
        self.form = frm_table_view(self, self.auth_manager, "users")
        self.form.exec()

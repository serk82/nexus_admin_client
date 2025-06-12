from controllers import AuthManager, UsersController
from lib.decorators import track_user_activity
from lib.exceptions import *
from lib.task_thread import LoadingDialog, TaskThread
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py import Ui_frm_notification_settings


@track_user_activity
class frm_notification_settings(QDialog):

    def __init__(self, form, auth_manager: AuthManager, user_id: int):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(form)
        self.users_controller = UsersController()
        self.user_id = user_id
        self.ui = Ui_frm_notification_settings()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.on_save_clicked)

        # Load data
        self.load_data()

    def collect_notifications_data(self):
        itv_expiry = (
            None
            if not self.ui.chb_itv_expiry.isChecked()
            or self.ui.sbx_itv_expiry.value() == 0
            else self.ui.sbx_itv_expiry.value()
        )
        tachograph_expiry = (
            None
            if not self.ui.chb_tachograph_expiry.isChecked()
            or self.ui.sbx_tachograph_expiry.value() == 0
            else self.ui.sbx_tachograph_expiry.value()
        )
        inspection_kms_expiry = (
            None
            if not self.ui.chb_inspection_kms_expiry.isChecked()
            or self.ui.sbx_inspection_kms_expiry.value() == 0
            else self.ui.sbx_inspection_kms_expiry.value()
        )
        return {
            "itv_expiry": itv_expiry,
            "tachograph_expiry": tachograph_expiry,
            "inspection_kms_expiry": inspection_kms_expiry,
        }

    def handle_error(self, error_message):
        self.loading_dialog.close()
        QMessageBox.warning(self, " ", error_message)
        self.setEnabled(True)

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
        self.loading_dialog.close()
        self.setEnabled(True)
        self.load_data()

    def save(self):
        notifications = self.collect_notifications_data()
        response = self.users_controller.update_user_notifications(
            self.auth_manager.token, self.user_id, notifications
        )
        if "error" in response:
            raise Exception(response.get("error"))

    def load_data(self):
        user = self.users_controller.get_user_by_id(
            self.auth_manager.token, self.user_id
        )
        if user.get("notification_itv_expiry") is None:
            self.ui.chb_itv_expiry.setChecked(False)
            self.ui.sbx_itv_expiry.setValue(0)
        else:
            self.ui.chb_itv_expiry.setChecked(True)
            self.ui.sbx_itv_expiry.setValue(user.get("notification_itv_expiry"))
        if user.get("notification_tachograph_expiry") is None:
            self.ui.chb_tachograph_expiry.setChecked(False)
            self.ui.sbx_tachograph_expiry.setValue(0)
        else:
            self.ui.chb_tachograph_expiry.setChecked(True)
            self.ui.sbx_tachograph_expiry.setValue(
                user.get("notification_tachograph_expiry")
            )
        if user.get("notification_inspection_kms_expiry") is None:
            self.ui.chb_inspection_kms_expiry.setChecked(False)
            self.ui.sbx_inspection_kms_expiry.setValue(0)
        else:
            self.ui.chb_inspection_kms_expiry.setChecked(True)
            self.ui.sbx_inspection_kms_expiry.setValue(
                user.get("notification_inspection_kms_expiry")
            )

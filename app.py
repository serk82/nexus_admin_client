import os, sys
from controllers import AuthManager
from PyQt6.QtWidgets import QApplication
from views.forms import (
    frm_login,
    frm_update,
    frm_vehicle,
    frm_table_view,
    frm_configuration,
    frm_main,
    frm_vehicles,
    frm_notifications,
    frm_options,
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Nexus-Admin")
    app.setDesktopFileName("Nexus-Admin")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(BASE_DIR, "lib", "styles.css")

    with open(css_path, "r") as file:
        app.setStyleSheet(file.read())

    # Check for updates
    # update_form = frm_update()
    # if update_form.check_update():
    #     update_form.exec()
    # login = frm_login()
    # login.show()

    auth_manager = AuthManager()
    if auth_manager.login("admin", "69ADM82s@"):
        # if auth_manager.login("carles", "1981"):

        form = frm_notifications(None, auth_manager, 1)
        form.exec()
        form = frm_options(auth_manager)
        form.show()

        # form = frm_configuration(auth_manager)
        # form.show()

        # form = frm_main(auth_manager, 4)
        # form.show()

        # form = frm_permissions(None, auth_manager)
        # form.show()

        # form = frm_table_view(None, auth_manager, "companies", 1)
        # form.show()

        # form = frm_vehicles(None, auth_manager, 4)
        # form.show()

        # form = frm_vehicle(None, auth_manager, True, 161, 4)
        # form.show()

    sys.exit(app.exec())

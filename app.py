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
    update_form = frm_update()
    if update_form.check_update():
        update_form.exec()
    login = frm_login()
    login.show()

    sys.exit(app.exec())

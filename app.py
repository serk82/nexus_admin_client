import os, sys
from controllers import AuthManager
from PyQt6.QtWidgets import QApplication
from views.forms import (
    frm_configuration,
    frm_login,
    frm_main,
    frm_table_view,
    frm_permissions,
    frm_update,
    frm_user,
    frm_vehicles,
    frm_vehicle,
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
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
    if auth_manager.login("admin", "1"):

        # form = frm_configuration(auth_manager)
        # form.show()

        # form = frm_main(None, 1)
        # form.show()

        # form = frm_permissions(None, auth_manager)
        # form.show()

        # form = frm_table_view(None, auth_manager, "companies", 1)
        # form.show()

        # form = frm_vehicles(None, auth_manager, 16)
        # form.show()

        form = frm_vehicle(None, auth_manager, True, 166, 16)
        form.show()

    sys.exit(app.exec())

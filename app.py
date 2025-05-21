import os, sys
from PyQt6.QtWidgets import QApplication
from views.forms import (
    frm_login,
    frm_update,
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
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

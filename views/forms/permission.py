from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py.permission import Ui_frm_permission


class frm_permission(QDialog):

    data_update = pyqtSignal()

    def __init__(self, form, edit, id):
        super().__init__(form)
        self.frm = form
        self.edit = edit
        self.id = id
        self.ui = Ui_frm_permission()
        self.ui.setupUi(self)

        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.setEnabled(False)
        # Events
        # self.ui.btn_close.clicked.connect(self.close)
        # self.ui.btn_save.clicked.connect(self.save)

        # if edit:
        #     self.setWindowTitle("Editar permiso")
        #     self.ui.btn_save.setText("Guardar")
        #     permission = Permission.get_permission(id)
        #     self.ui.txt_name.setText(permission.name)
        #     self.ui.txt_description.setText(permission.description)
        # else:
        #     self.setWindowTitle("Añadir permiso")
        #     self.ui.btn_save.setText("Añadir")

    def save(self):
        if self.edit:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres guardar los cambios?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                try:
                    if Permission.update(self.id, self.ui.txt_name.text().strip()):
                        self.data_update.emit()
                        self.close()
                    else:
                        QMessageBox.warning(self, " ", "Error al editar el rol.")
                except ValueError as e:
                    QMessageBox.warning(self, " ", str(e))
        else:
            answer = QMessageBox.question(
                self,
                " ",
                "Seguro quieres añadir el rol?",
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                # Add role
                try:
                    if Permission.add(self.ui.txt_name.text().strip()):
                        self.data_update.emit()
                        self.close()
                    else:
                        QMessageBox.warning(self, " ", "Error al crear el rol.")
                except ValueError as e:
                    QMessageBox.warning(self, " ", str(e))

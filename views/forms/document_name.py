from controllers import AuthManager
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QMessageBox
from views.forms_py import Ui_frm_document_name
from pathlib import Path


class frm_document_name(QDialog):
    
    document_name = pyqtSignal(str)
    
    def __init__(self, form, auth_manager: AuthManager, suffix: str):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)
        self.ui = Ui_frm_document_name()
        self.ui.setupUi(self)
        
        # Variables
        self.suffix = suffix
        
        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.save)
        
        # Tab Order
        self.setTabOrder(self.ui.txt_document_name, self.ui.btn_save)
        self.setTabOrder(self.ui.btn_save, self.ui.btn_close)
        self.ui.txt_document_name.setFocus()
        
    def save(self):
        if self.ui.txt_document_name.text():
            self.document_name.emit(f"{self.ui.txt_document_name.text()}{self.suffix}")
            self.close()
        else:
            QMessageBox.information(self, " ", "El campo 'nombre' no puede estar vacío.")

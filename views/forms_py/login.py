# Form implementation generated from reading ui file 'views/forms_ui/login.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_frm_login(object):
    def setupUi(self, frm_login):
        frm_login.setObjectName("frm_login")
        frm_login.resize(263, 313)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(frm_login)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        self.lbl_logo = QtWidgets.QLabel(parent=frm_login)
        self.lbl_logo.setMinimumSize(QtCore.QSize(0, 100))
        self.lbl_logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setObjectName("lbl_logo")
        self.verticalLayout_2.addWidget(self.lbl_logo)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.txt_username = QtWidgets.QLineEdit(parent=frm_login)
        self.txt_username.setObjectName("txt_username")
        self.verticalLayout.addWidget(self.txt_username)
        self.txt_password = QtWidgets.QLineEdit(parent=frm_login)
        self.txt_password.setObjectName("txt_password")
        self.verticalLayout.addWidget(self.txt_password)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.btn_exit = QtWidgets.QPushButton(parent=frm_login)
        self.btn_exit.setObjectName("btn_exit")
        self.horizontalLayout.addWidget(self.btn_exit)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.btn_login = QtWidgets.QPushButton(parent=frm_login)
        self.btn_login.setObjectName("btn_login")
        self.horizontalLayout.addWidget(self.btn_login)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.lbl_version = QtWidgets.QLabel(parent=frm_login)
        self.lbl_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_version.setObjectName("lbl_version")
        self.verticalLayout_2.addWidget(self.lbl_version)

        self.retranslateUi(frm_login)
        QtCore.QMetaObject.connectSlotsByName(frm_login)

    def retranslateUi(self, frm_login):
        _translate = QtCore.QCoreApplication.translate
        frm_login.setWindowTitle(_translate("frm_login", "Dialog"))
        self.lbl_logo.setText(_translate("frm_login", "LOGO"))
        self.txt_username.setPlaceholderText(_translate("frm_login", "Usuario"))
        self.txt_password.setPlaceholderText(_translate("frm_login", "Password"))
        self.btn_exit.setText(_translate("frm_login", "Salir"))
        self.btn_login.setText(_translate("frm_login", "Entrar"))
        self.lbl_version.setText(_translate("frm_login", "VERSION"))

# Form implementation generated from reading ui file 'views/forms_ui/user.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_frm_user(object):
    def setupUi(self, frm_user):
        frm_user.setObjectName("frm_user")
        frm_user.resize(456, 582)
        self.gridLayout_4 = QtWidgets.QGridLayout(frm_user)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(parent=frm_user)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lbl_user = QtWidgets.QLabel(parent=self.groupBox)
        self.lbl_user.setObjectName("lbl_user")
        self.gridLayout_2.addWidget(self.lbl_user, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        self.lbl_role = QtWidgets.QLabel(parent=self.groupBox)
        self.lbl_role.setObjectName("lbl_role")
        self.gridLayout_2.addWidget(self.lbl_role, 4, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.txt_username = QtWidgets.QLineEdit(parent=self.groupBox)
        self.txt_username.setObjectName("txt_username")
        self.gridLayout.addWidget(self.txt_username, 0, 0, 1, 1)
        self.txt_name = QtWidgets.QLineEdit(parent=self.groupBox)
        self.txt_name.setObjectName("txt_name")
        self.gridLayout.addWidget(self.txt_name, 1, 0, 1, 1)
        self.txt_lastname = QtWidgets.QLineEdit(parent=self.groupBox)
        self.txt_lastname.setObjectName("txt_lastname")
        self.gridLayout.addWidget(self.txt_lastname, 2, 0, 1, 1)
        self.txt_email = QtWidgets.QLineEdit(parent=self.groupBox)
        self.txt_email.setObjectName("txt_email")
        self.gridLayout.addWidget(self.txt_email, 3, 0, 1, 1)
        self.cmb_role = QtWidgets.QComboBox(parent=self.groupBox)
        self.cmb_role.setObjectName("cmb_role")
        self.gridLayout.addWidget(self.cmb_role, 4, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.twd_companies = QtWidgets.QTableWidget(parent=self.groupBox)
        self.twd_companies.setObjectName("twd_companies")
        self.twd_companies.setColumnCount(0)
        self.twd_companies.setRowCount(0)
        self.gridLayout_3.addWidget(self.twd_companies, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.btn_close = QtWidgets.QPushButton(parent=frm_user)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout_4.addWidget(self.btn_close)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.btn_save = QtWidgets.QPushButton(parent=frm_user)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout_4.addWidget(self.btn_save)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.gridLayout_4.addLayout(self.horizontalLayout_4, 4, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btn_reset_password = QtWidgets.QPushButton(parent=frm_user)
        self.btn_reset_password.setObjectName("btn_reset_password")
        self.verticalLayout.addWidget(self.btn_reset_password)
        self.gridLayout_4.addLayout(self.verticalLayout, 2, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_4.addItem(spacerItem4, 1, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_4.addItem(spacerItem5, 3, 0, 1, 1)

        self.retranslateUi(frm_user)
        QtCore.QMetaObject.connectSlotsByName(frm_user)

    def retranslateUi(self, frm_user):
        _translate = QtCore.QCoreApplication.translate
        frm_user.setWindowTitle(_translate("frm_user", "Usuario"))
        self.groupBox.setTitle(_translate("frm_user", "Datos"))
        self.lbl_user.setText(_translate("frm_user", "Usuario"))
        self.label.setText(_translate("frm_user", "Nombre"))
        self.label_2.setText(_translate("frm_user", "Apellidos"))
        self.label_3.setText(_translate("frm_user", "E-mail"))
        self.lbl_role.setText(_translate("frm_user", "Rol"))
        self.btn_close.setText(_translate("frm_user", "Cerrar"))
        self.btn_save.setText(_translate("frm_user", "Guardar"))
        self.btn_reset_password.setText(_translate("frm_user", "Resetear Contraseña"))

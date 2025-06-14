# Form implementation generated from reading ui file 'views/forms_ui/notification_settings.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_frm_notification_settings(object):
    def setupUi(self, frm_notification_settings):
        frm_notification_settings.setObjectName("frm_notification_settings")
        frm_notification_settings.resize(406, 224)
        self.gridLayout_2 = QtWidgets.QGridLayout(frm_notification_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_close = QtWidgets.QPushButton(parent=frm_notification_settings)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout.addWidget(self.btn_close)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_save = QtWidgets.QPushButton(parent=frm_notification_settings)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout.addWidget(self.btn_save)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 1, 0, 1, 1)
        self.gbx_notification_settings = QtWidgets.QGroupBox(parent=frm_notification_settings)
        self.gbx_notification_settings.setCheckable(False)
        self.gbx_notification_settings.setObjectName("gbx_notification_settings")
        self.gridLayout = QtWidgets.QGridLayout(self.gbx_notification_settings)
        self.gridLayout.setObjectName("gridLayout")
        self.chb_itv_expiry = QtWidgets.QCheckBox(parent=self.gbx_notification_settings)
        self.chb_itv_expiry.setObjectName("chb_itv_expiry")
        self.gridLayout.addWidget(self.chb_itv_expiry, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sbx_itv_expiry = QtWidgets.QSpinBox(parent=self.gbx_notification_settings)
        self.sbx_itv_expiry.setObjectName("sbx_itv_expiry")
        self.horizontalLayout_2.addWidget(self.sbx_itv_expiry)
        self.lbl_itv_expiry = QtWidgets.QLabel(parent=self.gbx_notification_settings)
        self.lbl_itv_expiry.setObjectName("lbl_itv_expiry")
        self.horizontalLayout_2.addWidget(self.lbl_itv_expiry)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.chb_tachograph_expiry = QtWidgets.QCheckBox(parent=self.gbx_notification_settings)
        self.chb_tachograph_expiry.setObjectName("chb_tachograph_expiry")
        self.gridLayout.addWidget(self.chb_tachograph_expiry, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sbx_tachograph_expiry = QtWidgets.QSpinBox(parent=self.gbx_notification_settings)
        self.sbx_tachograph_expiry.setObjectName("sbx_tachograph_expiry")
        self.horizontalLayout_4.addWidget(self.sbx_tachograph_expiry)
        self.lbl_tachograph_expiry = QtWidgets.QLabel(parent=self.gbx_notification_settings)
        self.lbl_tachograph_expiry.setObjectName("lbl_tachograph_expiry")
        self.horizontalLayout_4.addWidget(self.lbl_tachograph_expiry)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.chb_inspection_kms_expiry = QtWidgets.QCheckBox(parent=self.gbx_notification_settings)
        self.chb_inspection_kms_expiry.setObjectName("chb_inspection_kms_expiry")
        self.gridLayout.addWidget(self.chb_inspection_kms_expiry, 2, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.sbx_inspection_kms_expiry = QtWidgets.QSpinBox(parent=self.gbx_notification_settings)
        self.sbx_inspection_kms_expiry.setMaximum(999999)
        self.sbx_inspection_kms_expiry.setSingleStep(100)
        self.sbx_inspection_kms_expiry.setObjectName("sbx_inspection_kms_expiry")
        self.horizontalLayout_3.addWidget(self.sbx_inspection_kms_expiry)
        self.lbl_inspection_kms_expiry = QtWidgets.QLabel(parent=self.gbx_notification_settings)
        self.lbl_inspection_kms_expiry.setObjectName("lbl_inspection_kms_expiry")
        self.horizontalLayout_3.addWidget(self.lbl_inspection_kms_expiry)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.gbx_notification_settings, 0, 0, 1, 1)

        self.retranslateUi(frm_notification_settings)
        QtCore.QMetaObject.connectSlotsByName(frm_notification_settings)

    def retranslateUi(self, frm_notification_settings):
        _translate = QtCore.QCoreApplication.translate
        frm_notification_settings.setWindowTitle(_translate("frm_notification_settings", "Configuración de notificaciones"))
        self.btn_close.setText(_translate("frm_notification_settings", "Cerrar"))
        self.btn_save.setText(_translate("frm_notification_settings", "Guardar"))
        self.gbx_notification_settings.setTitle(_translate("frm_notification_settings", "Notificaciones al inicio"))
        self.chb_itv_expiry.setText(_translate("frm_notification_settings", "Caducidad ITV"))
        self.lbl_itv_expiry.setText(_translate("frm_notification_settings", "días antes"))
        self.chb_tachograph_expiry.setText(_translate("frm_notification_settings", "Caducidad Tacógrafo"))
        self.lbl_tachograph_expiry.setText(_translate("frm_notification_settings", "días antes"))
        self.chb_inspection_kms_expiry.setText(_translate("frm_notification_settings", "Revision por KMS"))
        self.lbl_inspection_kms_expiry.setText(_translate("frm_notification_settings", "kms antes"))

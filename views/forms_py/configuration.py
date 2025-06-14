# Form implementation generated from reading ui file 'views/forms_ui/configuration.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_frm_configuration(object):
    def setupUi(self, frm_configuration):
        frm_configuration.setObjectName("frm_configuration")
        frm_configuration.resize(800, 600)
        frm_configuration.setMouseTracking(False)
        self.centralwidget = QtWidgets.QWidget(parent=frm_configuration)
        self.centralwidget.setObjectName("centralwidget")
        frm_configuration.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=frm_configuration)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menu_archive = QtWidgets.QMenu(parent=self.menubar)
        self.menu_archive.setObjectName("menu_archive")
        self.menu_configuration = QtWidgets.QMenu(parent=self.menubar)
        self.menu_configuration.setObjectName("menu_configuration")
        self.menu_Seguridad = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Seguridad.setObjectName("menu_Seguridad")
        frm_configuration.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=frm_configuration)
        self.statusbar.setMouseTracking(False)
        self.statusbar.setObjectName("statusbar")
        frm_configuration.setStatusBar(self.statusbar)
        self.action_exit = QtGui.QAction(parent=frm_configuration)
        self.action_exit.setObjectName("action_exit")
        self.action_companies = QtGui.QAction(parent=frm_configuration)
        self.action_companies.setObjectName("action_companies")
        self.action_users = QtGui.QAction(parent=frm_configuration)
        self.action_users.setObjectName("action_users")
        self.action_roles = QtGui.QAction(parent=frm_configuration)
        self.action_roles.setObjectName("action_roles")
        self.action_permissions = QtGui.QAction(parent=frm_configuration)
        self.action_permissions.setObjectName("action_permissions")
        self.action_close_session = QtGui.QAction(parent=frm_configuration)
        self.action_close_session.setObjectName("action_close_session")
        self.action_change_company = QtGui.QAction(parent=frm_configuration)
        self.action_change_company.setObjectName("action_change_company")
        self.actionEmpleados = QtGui.QAction(parent=frm_configuration)
        self.actionEmpleados.setObjectName("actionEmpleados")
        self.actionVeh_culos = QtGui.QAction(parent=frm_configuration)
        self.actionVeh_culos.setObjectName("actionVeh_culos")
        self.action_Tipos_de_documentos_empleados = QtGui.QAction(parent=frm_configuration)
        self.action_Tipos_de_documentos_empleados.setObjectName("action_Tipos_de_documentos_empleados")
        self.action_workorder_document_types = QtGui.QAction(parent=frm_configuration)
        self.action_workorder_document_types.setObjectName("action_workorder_document_types")
        self.action_Copia_de_seguridad = QtGui.QAction(parent=frm_configuration)
        self.action_Copia_de_seguridad.setObjectName("action_Copia_de_seguridad")
        self.action_Tipos_de_documento = QtGui.QAction(parent=frm_configuration)
        self.action_Tipos_de_documento.setObjectName("action_Tipos_de_documento")
        self.action_notifications = QtGui.QAction(parent=frm_configuration)
        self.action_notifications.setObjectName("action_notifications")
        self.menu_archive.addAction(self.action_change_company)
        self.menu_archive.addAction(self.action_close_session)
        self.menu_archive.addAction(self.action_exit)
        self.menu_configuration.addSeparator()
        self.menu_configuration.addAction(self.action_companies)
        self.menu_configuration.addAction(self.action_permissions)
        self.menu_configuration.addAction(self.action_roles)
        self.menu_configuration.addAction(self.action_users)
        self.menu_configuration.addAction(self.action_notifications)
        self.menu_Seguridad.addAction(self.action_Copia_de_seguridad)
        self.menubar.addAction(self.menu_archive.menuAction())
        self.menubar.addAction(self.menu_configuration.menuAction())
        self.menubar.addAction(self.menu_Seguridad.menuAction())

        self.retranslateUi(frm_configuration)
        QtCore.QMetaObject.connectSlotsByName(frm_configuration)

    def retranslateUi(self, frm_configuration):
        _translate = QtCore.QCoreApplication.translate
        frm_configuration.setWindowTitle(_translate("frm_configuration", "Plataforma Empresa"))
        self.menu_archive.setTitle(_translate("frm_configuration", "&Archivo"))
        self.menu_configuration.setTitle(_translate("frm_configuration", "&Configuración"))
        self.menu_Seguridad.setTitle(_translate("frm_configuration", "&Seguridad"))
        self.action_exit.setText(_translate("frm_configuration", "&Salir"))
        self.action_companies.setText(_translate("frm_configuration", "&Empresas"))
        self.action_users.setText(_translate("frm_configuration", "&Usuarios"))
        self.action_roles.setText(_translate("frm_configuration", "&Roles"))
        self.action_permissions.setText(_translate("frm_configuration", "&Permisos"))
        self.action_close_session.setText(_translate("frm_configuration", "&Cerrar sesión"))
        self.action_change_company.setText(_translate("frm_configuration", "&Cambiar de empresa"))
        self.actionEmpleados.setText(_translate("frm_configuration", "Empleados"))
        self.actionVeh_culos.setText(_translate("frm_configuration", "Vehículos"))
        self.action_Tipos_de_documentos_empleados.setText(_translate("frm_configuration", "&Tipos de documento"))
        self.action_workorder_document_types.setText(_translate("frm_configuration", "&Tipos de documento"))
        self.action_Copia_de_seguridad.setText(_translate("frm_configuration", "&Copia de seguridad"))
        self.action_Tipos_de_documento.setText(_translate("frm_configuration", "&Tipos de documento"))
        self.action_notifications.setText(_translate("frm_configuration", "&Notificaciones"))

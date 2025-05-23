import subprocess, shutil, platform
from controllers import AuthManager
from datetime import date
from lib.config import API_HOST
from lib.task_thread import TaskThread
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.QtCore import QEventLoop
from views.forms_py import Ui_frm_backup


class frm_backup(QDialog):

    def __init__(self, form, auth_manager: AuthManager):
        super().__init__(form)
        self.auth_manager = auth_manager
        self.auth_manager.is_token_expired(self)

        # Load UI
        self.ui = Ui_frm_backup()
        self.ui.setupUi(self)

        # Events
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_backup.clicked.connect(self.on_backup)
        self.ui.btn_dialog.clicked.connect(self.show_dialog)

        self.ui.progressBar.setValue(0)
        self.ui.progressBar_total.setValue(0)
        self.ui.txt_target.setReadOnly(True)

    def backup(self):
        try:
            num_workers = 3
            self.hilo.messages.emit("Preparando copia de seguridad...")
            if not self.check_or_install_mysqldump():
                return
            self.hilo.total_progress.emit(1 * 100 // num_workers)
            self.path_folder = Path(self.target)
            self.path_folder = self.path_folder / "Backup_Nexus_Admin"
            self.hilo.messages.emit(
                f"Creando carpeta para las copias de seguridad: {self.path_folder}"
            )
            self.path_folder.mkdir(parents=True, exist_ok=True)
            self.path_folder_today = Path(self.path_folder / f"{date.today()}")
            self.hilo.messages.emit(
                f"Creando carpeta para la copia de hoy {date.today().day}/{date.today().month}/{date.today().year}:\n{self.path_folder_today}"
            )
            self.path_folder_today.mkdir(parents=True, exist_ok=True)

            self.backup_mysql()
            self.hilo.total_progress.emit(2 * 100 // num_workers)
            self.backup_files()
            self.hilo.total_progress.emit(3 * 100 // num_workers)
            self.hilo.messages.emit("")
            self.hilo.working.emit("¡Copia de seguridad realizada satisfactoriamente!")
        except subprocess.CalledProcessError as e:
            self.hilo.error.emit(f"Error al respaldar:\n{e.stderr}")
            self.hilo.messages.emit("")
            self.hilo.working.emit("¡Copia de seguridad NO realizada!")
        except Exception as e:
            self.hilo.error.emit(str(e))
            self.hilo.messages.emit("")
            self.hilo.working.emit("¡Copia de seguridad NO realizada!")

    def backup_files(self):
        try:
            self.hilo.progress.emit(0)
            self.hilo.working.emit(
                "Iniciando copia de seguridad de carpetas y archivos..."
            )
            source = Path("/srv/nexus_admin")
            dest = self.path_folder_today

            files = [f for f in source.rglob("*") if f.is_file()]

            total = len(files)

            for i, file_path in enumerate(files, 1):
                relative_path = file_path.relative_to(source)
                dest_file_path = dest / relative_path
                dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_file_path)

                self.hilo.progress.emit(i * 100 // total)

        except Exception as e:
            self.hilo.error.emit(str(e))

    def backup_mysql(self):
        try:
            self.hilo.progress.emit(0)
            self.hilo.working.emit(
                "Iniciando copia de seguridad de la base de datos..."
            )
            output_file = "database.sql"
            self.hilo.messages.emit(
                f"Creando copia de la base de datos en: {output_file}"
            )
            cmd = [
                "mysqldump",
                f"-u{self.ui.txt_username.text()}",
                f"-p{self.ui.txt_password.text()}",
                "-h",
                API_HOST,
                "nexus_admin",
            ]
            with open(self.path_folder_today / output_file, "w") as f:
                subprocess.run(
                    cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True
                )
            self.hilo.progress.emit(100)
            self.hilo.messages.emit(f"Respaldo completado:\n{output_file}")
        except subprocess.CalledProcessError as e:
            self.hilo.error.emit(f"Error al respaldar:\n{e.stderr}")
            self.hilo.messages.emit("")
            self.hilo.working.emit("¡Copia de seguridad NO realizada!")
        except Exception as e:
            self.hilo.error.emit(str(e))
            self.hilo.messages.emit("")
            self.hilo.working.emit("¡Copia de seguridad NO realizada!")

    def check_or_install_mysqldump(self):
        loop = QEventLoop()
        self.response = None

        def receive_response(r):
            self.response = r
            loop.quit()

        self.hilo.progress.emit(0)
        num_workers = 2
        if self.is_mysqldump_available():
            return True
        self.hilo.progress.emit(1 * 100 // num_workers)

        system = platform.system()

        if system == "Windows":
            self.hilo.show_message_info.emit(
                "Error",
                "No se encontró mysqldump en tu sistema.\n\n"
                "Por favor instala MySQL desde:\n"
                "https://dev.mysql.com/downloads/mysql/",
            )
            self.hilo.response_message.connect(receive_response)
            loop.exec()
            return False

        elif system == "Linux":
            self.hilo.show_message_response.emit(
                "Instalar mysqldump",
                "mysqldump no está instalado.\n¿Deseas instalarlo ahora con apt?",
            )
            self.hilo.response_message.connect(receive_response)
            loop.exec()
            if self.response:
                try:
                    subprocess.run(
                        ["pkexec", "apt", "install", "-y", "mysql-client"], check=True
                    )
                    self.hilo.progress.emit(2 * 100 // num_workers)
                    return self.is_mysqldump_available()
                except Exception as e:
                    self.hilo.show_message_info.emit(
                        "Error", f"No se pudo instalar mysqldump:\n{e}"
                    )
                    self.hilo.response_message.connect(receive_response)
                    loop.exec()
                    return False

    def is_mysqldump_available(self):
        return shutil.which("mysqldump") is not None

    def handle_ask_user(self, title, message):
        response = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        self.hilo.response_message.emit(response == QMessageBox.StandardButton.Yes)

    def handle_error(self, error_message):
        QMessageBox.warning(self, "Error", error_message)

    def handle_info_user(self, title, message):
        QMessageBox.question(
            self,
            title,
            message,
        )

    def on_backup(self):
        self.auth_manager.is_token_expired(self)
        if not self.ui.txt_target.text():
            QMessageBox.information(
                self,
                " ",
                "Por favor, selecciona una carpeta de destino.",
            )
            self.ui.txt_target.setFocus()
            return
        self.ui.btn_backup.setEnabled(False)
        self.ui.btn_dialog.setEnabled(False)
        self.ui.btn_close.setEnabled(False)
        self.hilo = TaskThread(self.backup)
        self.hilo.progress.connect(self.ui.progressBar.setValue)
        self.hilo.total_progress.connect(self.ui.progressBar_total.setValue)
        self.hilo.working.connect(self.ui.txt_messages.setText)
        self.hilo.messages.connect(self.ui.txt_copy_target.setText)
        self.hilo.show_message_response.connect(self.handle_ask_user)
        self.hilo.show_message_info.connect(self.handle_info_user)
        self.hilo.error.connect(self.handle_error)
        self.hilo.finished.connect(self.on_task_finished)
        self.hilo.start()

    def on_task_finished(self):
        self.ui.btn_backup.setEnabled(True)
        self.ui.btn_dialog.setEnabled(True)
        self.ui.btn_close.setEnabled(True)

    def show_dialog(self):
        self.auth_manager.is_token_expired(self)
        self.target = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de destino",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if self.target:
            self.ui.txt_target.setText(self.target)

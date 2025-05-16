import os
import sys
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from packaging import version

REPO_USER = "serk82"
REPO_NAME = "nexus_admin_client"
VERSION_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "__version__.py")
)
APP_FOLDER = os.path.abspath(".")


class frm_update(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Actualización disponible")
        self.setFixedSize(400, 200)

        self.layout = QVBoxLayout(self)
        self.label_current = QLabel("Versión actual: ...")
        self.label_latest = QLabel("Última versión: ...")
        self.label_status = QLabel("")
        self.label_status.setWordWrap(True)
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_update = QPushButton("Actualizar ahora")
        self.button_update.setEnabled(False)

        self.layout.addWidget(self.label_current)
        self.layout.addWidget(self.label_latest)
        self.layout.addWidget(self.label_status)
        self.layout.addWidget(self.button_update)

        self.button_update.clicked.connect(self.perform_update)

        self.latest_version = None
        self.latest_asset = None
        self.setStyleSheet("font-size: 14px;")

    def closeEvent(self, event):
        if event.isAccepted():
            QMessageBox.warning(
                self,
                "Advertencia",
                "Debes actualizar la aplicación para inicar.",
            )
            sys.exit(0)

    def get_local_version(self):
        try:
            version_path = VERSION_FILE
            version_globals = {}
            with open(version_path, "r") as f:
                exec(f.read(), version_globals)
            return version_globals["version"]
        except Exception as e:
            return e

    def check_update(self):
        self.label_status.setText("Buscando nueva versión...")
        local_ver = self.get_local_version()
        self.label_current.setText(f"Versión actual: {local_ver}")
        try:
            url = (
                f"https://api.github.com/repos/{REPO_USER}/{REPO_NAME}/releases/latest"
            )
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            latest_ver = data["tag_name"].lstrip("v")
            self.label_latest.setText(f"Última versión: {latest_ver}")
            self.latest_version = latest_ver

            if version.parse(latest_ver) > version.parse(local_ver):
                self.label_status.setText("🔔 ¡Nueva versión disponible!")
                self.button_update.setEnabled(True)
                # Utilizar zipball_url
                self.latest_asset = data.get("zipball_url")
                return True
            else:
                # self.label_status.setText("✅ Ya tienes la última versión.")
                return False
        except Exception as e:
            self.label_status.setText(f"❌ Error: {str(e)}")

    def perform_update(self):
        if not self.latest_asset:
            QMessageBox.warning(self, "Error", "No se encontró archivo para descargar.")
            return

        self.label_status.setText("⬇️ Descargando nueva versión...")
        app_zip_path = os.path.join("/tmp", "app_update.zip")
        extract_dir = os.path.join("/tmp", "app_update")

        try:
            r = requests.get(self.latest_asset, stream=True)
            with open(app_zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with zipfile.ZipFile(app_zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Buscar la carpeta principal extraída (suele ser única)
            subfolders = [os.path.join(extract_dir, d) for d in os.listdir(extract_dir)]
            if subfolders:
                extracted_root = subfolders[0]  # primera carpeta
            else:
                raise RuntimeError("No se encontró contenido extraído.")

            # Sustituir archivos de la aplicación
            for item in os.listdir(extracted_root):
                src = os.path.join(extracted_root, item)
                dst = os.path.join(APP_FOLDER, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            # Actualizar versión
            with open(VERSION_FILE, "w") as f:
                f.write(f'version = "{self.latest_version}"\n')

            QMessageBox.information(
                self, "Actualizado", "✅ Aplicación actualizada. Se reiniciará."
            )
            self.restart_app()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def restart_app(self):
        self.close()
        python = sys.executable
        os.execl(python, python, *sys.argv)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = frm_update()
    ventana.show()
    sys.exit(app.exec())

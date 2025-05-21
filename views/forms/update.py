from pathlib import Path
import sys, subprocess, requests, zipfile, shutil, json
from packaging import version
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

REPO_USER = "serk82"
REPO_NAME = "nexus_admin_client"
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"
APP_FOLDER = Path.cwd() / "nexus_admin_client"

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

        self.actualized = False

        self.button_update.clicked.connect(self.perform_update)

        self.latest_version = None
        self.latest_asset = None
        self.setStyleSheet("font-size: 14px;")
        self.check_update()

    def closeEvent(self, event):
        if event.isAccepted():
            response = QMessageBox.warning(
                self,
                "Advertencia",
                "No puedes iniciar la aplicación sin actualizar. ¿Quieres salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if response == QMessageBox.StandardButton.Yes:
                sys.exit(0)
            else:
                event.ignore()

    def get_local_version(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            return e

    def set_local_version(self, data):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"VERSION": data}, f, indent=4)

    def check_update(self):
        self.label_status.setText("Buscando nueva versión...")
        local_ver = self.get_local_version()["VERSION"]
        self.label_current.setText(f"Versión actual: {local_ver}")
        try:
            url = f"https://api.github.com/repos/{REPO_USER}/{REPO_NAME}/releases/latest"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            latest_ver = data["tag_name"].lstrip("v")
            self.label_latest.setText(f"Última versión: {latest_ver}")
            self.latest_version = latest_ver

            if version.parse(latest_ver) > version.parse(local_ver):
                self.label_status.setText("🔔 ¡Nueva versión disponible!")
                self.button_update.setEnabled(True)
                self.latest_asset = data.get("zipball_url")
                return True
            else:
                self.label_status.setText("✅ Ya tienes la última versión.")
                return False
        except Exception as e:
            self.label_status.setText(f"❌ Error: {str(e)}")

    def perform_update(self):
        if not self.latest_asset:
            QMessageBox.warning(self, "Error", "No se encontró archivo para descargar.")
            return

        self.label_status.setText("⬇️ Descargando nueva versión...")

        tmp_dir = APP_FOLDER / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        app_zip_path = tmp_dir / "app_update.zip"
        extract_dir = tmp_dir / "app_update"

        try:
            r = requests.get(self.latest_asset, stream=True)
            with open(app_zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with zipfile.ZipFile(app_zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            subfolders = [f for f in extract_dir.iterdir() if f.is_dir()]
            if subfolders:
                extracted_root = subfolders[0]
            else:
                raise RuntimeError("No se encontró contenido extraído.")

            for item in extracted_root.iterdir():
                dst = APP_FOLDER / item.name
                if item.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)

            self.set_local_version(self.latest_version)

            if app_zip_path.exists():
                app_zip_path.unlink()
            if extract_dir.exists():
                shutil.rmtree(extract_dir)

            QMessageBox.information(
                self, "Actualizado", "✅ Aplicación actualizada. Se reiniciará."
            )
            self.restart_app()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def restart_app(self):
        app_path = Path.cwd() / "nexus_admin_client" / "app.py"
        subprocess.Popen([sys.executable, str(app_path)])
        QApplication.quit()
        sys.exit()

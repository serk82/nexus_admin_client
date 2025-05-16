import jwt, requests, sys, subprocess
from datetime import datetime, timezone
from lib.config import API_HOST, API_PORT
from lib.exceptions import *
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
)


class AuthManager:
    def __init__(self):
        self.token = None
        self.role_id = None
        self.username = None

    def is_token_expired(self, window=None):
        if not self.token:
            self.redirect_to_login(window)
        try:
            payload = jwt.decode(self.token, options={"verify_signature": False})
            expiration = payload.get("exp")
            if expiration:
                exp_datetime = datetime.fromtimestamp(expiration, tz=timezone.utc)
                if exp_datetime < datetime.now(timezone.utc):
                    self.redirect_to_login(window)
        except jwt.ExpiredSignatureError:
            self.redirect_to_login(window)
        except jwt.InvalidTokenError:
            self.redirect_to_login(window)

    def has_permission(self, permission_code):
        url = f"http://{API_HOST}:{API_PORT}/roles/{self.role_id}/permissions"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                premissions = response.json()
                for permission in premissions:
                    if permission == permission_code or permission == "CT":
                        return True
                return False
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error de conexión: {str(e)}")

    def login(self, username, password):
        url = f"http://{API_HOST}:{API_PORT}/users/login/"
        data = {"username": username, "password": password}
        try:
            response = requests.get(url, json=data)
            if response.status_code == 200:
                login = response.json()
                self.token = login['token']
                self.role_id = int(login['role_id'])
                self.username = username
                return True
            else:
                return False
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error de conexión: {str(e)}")

    def redirect_to_login(self, window=None):
        QMessageBox.information(
            window,
            " ",
            "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
        )
        QApplication.quit()
        subprocess.Popen([sys.executable, "nexus_admin_client/app.py"])
        sys.exit()

    def logout(self):
        self.token = None
        self.role_id = None
        self.redirect_to_login()

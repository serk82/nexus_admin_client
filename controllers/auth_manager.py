import jwt, requests, sys, subprocess, time
from datetime import datetime, timezone, timedelta
from lib.config import API_HOST, API_PORT
from lib.exceptions import *
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
)


class AuthManager:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.username = None
        self.role_id = None
        self.permissions = None
        self.last_activity_time = datetime.now(timezone.utc)
        self.inactivity_limit = None

    def is_token_expired(self, window=None):
        if not self.token:
            self.redirect_to_login(window)
            return True
        try:
            payload = jwt.decode(self.token, options={"verify_signature": False})
            expiration = payload.get("exp")
            if expiration:
                exp_datetime = datetime.fromtimestamp(expiration, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                if (
                    exp_datetime < datetime.now(timezone.utc)
                    or now - self.last_activity_time > self.inactivity_limit
                ):
                    self.redirect_to_login(window)
                    return True
        except jwt.ExpiredSignatureError:
            self.redirect_to_login(window)
            return True
        except jwt.InvalidTokenError:
            self.redirect_to_login(window)
            return True
        return False

    def has_permission(self, permission_code):
        for permission in self.permissions:
            if permission == permission_code or permission == "CT":
                return True
        return False

    def login(self, username, password):
        url = f"http://{API_HOST}:{API_PORT}/users/login/"
        data = {"username": username, "password": password}
        try:
            response = requests.get(url, json=data)
            if response.status_code == 200:
                login = response.json()
                self.token = login["token"]
                self.user_id = int(login["id"])
                self.username = username
                self.role_id = int(login["role_id"])
                self.permissions = login["permissions"]
                self.inactivity_limit = timedelta(seconds=float(login["inactivity"]))
                return True
            else:
                return False
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error de conexión: {str(e)}")

    def record_activity(self):
        self.last_activity_time = datetime.now(timezone.utc)

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

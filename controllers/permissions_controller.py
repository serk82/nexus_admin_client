import requests
from lib.config import API_HOST, API_PORT


class PermissionsController:

    def get_permission(self, token, permission_code):
        url = f"http://{API_HOST}:{API_PORT}/permissions/{permission_code}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_permissions(self, token):
        url = f"http://{API_HOST}:{API_PORT}/permissions/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

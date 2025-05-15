import requests
from lib.config import API_HOST, API_PORT


class UsersController:

    def add_user(self, token, user: dict):
        url = f"http://{API_HOST}:{API_PORT}/users/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(url, json=user, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Usuario no encontrado"}
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_user_by_id(self, token, user_id):
        url = f"http://{API_HOST}:{API_PORT}/users/{user_id}"
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

    def get_users(self, token):
        url = f"http://{API_HOST}:{API_PORT}/users/"
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
        
    def some_user_has_role(self, token, role_id):
        url = f"http://{API_HOST}:{API_PORT}/users/role/{role_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(response.json())
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def update_user(self, token, user: dict):
        url = f"http://{API_HOST}:{API_PORT}/users/{user.get('id')}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.put(url, json=user, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Usuario no encontrado"}
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

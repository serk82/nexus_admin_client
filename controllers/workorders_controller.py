import requests
from lib.config import API_HOST, API_PORT


class WorkOrdersController:

    def add_workorder(self, token, workorder: dict):
        url = f"http://{API_HOST}:{API_PORT}/workorders/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(url, headers=headers, json=workorder)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                return response.json().get("detail")
            elif response.status_code == 409:
                return response.json().get("detail")
            elif response.status_code == 422:
                return {
                    "error": f"Datos inválidos enviados: {response.json().get('detail')}"
                }
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_document(self, token, subfolder, filename):
        url = f"http://{API_HOST}:{API_PORT}/files/"
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        params["subfolder"] = subfolder
        params["filename"] = filename
        try:
            response = requests.delete(url, headers=headers, json=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                return response.json().get("detail")
            elif response.status_code == 422:
                return {
                    "error": f"Datos inválidos enviados: {response.json().get('detail')}"
                }
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_workorder(self, token, workorder_id):
        url = f"http://{API_HOST}:{API_PORT}/workorders/{workorder_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                return response.json().get("detail")
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_first_workorder(self, token, vehicle_id):
        url = f"http://{API_HOST}:{API_PORT}/workorders/first/{vehicle_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
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

    def get_last_workorder(self, token, vehicle_id):
        url = f"http://{API_HOST}:{API_PORT}/workorders/last/{vehicle_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
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

    def get_file(self, token, subfolder, filename):
        url = (
            f"http://{API_HOST}:{API_PORT}/files/files/{filename}?subfolder={subfolder}"
        )
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            elif response.status_code == 404:
                return response.json().get("detail")
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_documents(self, token, subfolder):
        url = f"http://{API_HOST}:{API_PORT}/files/"
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        params["subfolder"] = subfolder
        try:
            response = requests.get(url, headers=headers, json=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            elif response.status_code == 404:
                return {"error": response.json().get("detail")}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_workorder(self, token, workorder_id):
        url = f"http://{API_HOST}:{API_PORT}/workorders/{workorder_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            elif response.status_code == 404:
                return response.json().get("detail")
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_workorders(
        self, token, vehicle_id, date_from=None, date_to=None, search=None
    ):
        url = f"http://{API_HOST}:{API_PORT}/workorders/vehicles/{vehicle_id}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if search:
            params["search"] = search
        try:
            response = requests.get(url, headers=headers, json=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            elif response.status_code == 404:
                return response.json().get("detail")
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def update_workorder(self, token, workorder: dict):
        url = f"http://{API_HOST}:{API_PORT}/workorders/{workorder.get('id')}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.put(url, headers=headers, json=workorder)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                return response.json().get("detail")
            elif response.status_code == 409:
                return response.json().get("detail")
            elif response.status_code == 422:
                return {
                    "error": f"Datos inválidos enviados: {response.json().get('detail')}"
                }
            else:
                return {"error": f"Error inesperado: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"message": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

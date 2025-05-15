import requests
from lib.config import API_HOST, API_PORT


class InspectionsController:

    def add_inspection(self, token, inspection: dict):
        url = f"http://{API_HOST}:{API_PORT}/inspections/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(url, headers=headers, json=inspection)
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

    def delete_inspection(self, token, inspection_id):
        url = f"http://{API_HOST}:{API_PORT}/inspections/{inspection_id}"
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

    def get_inspection(self, token, inspection_id):
        url = f"http://{API_HOST}:{API_PORT}/inspections/{inspection_id}"
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

    def get_inspections(self, token, vehicle_id=None):
        if vehicle_id:
            url = f"http://{API_HOST}:{API_PORT}/inspections/vehicles/{vehicle_id}"
        else:
            url = f"http://{API_HOST}:{API_PORT}/inspections/"
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

    def get_last_inspection(self, token, vehicle_id):
        url = f"http://{API_HOST}:{API_PORT}/inspections/last/{vehicle_id}"
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

    def update_inspection(self, token, inspection: dict):
        url = f"http://{API_HOST}:{API_PORT}/inspections/{inspection.get('id')}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.put(url, headers=headers, json=inspection)
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

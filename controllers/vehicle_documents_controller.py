import requests
from lib.config import API_HOST, API_PORT


class VehicleDocumentsController:

    def add_vehicle_document(self, token, vehicle_document: dict):
        url = f"http://{API_HOST}:{API_PORT}/vehicle_documents/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(url, json=vehicle_document, headers=headers)
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

    def delete_vehicle_document(self, token, vehicle_document_id):
        url = f"http://{API_HOST}:{API_PORT}/vehicle_documents/{vehicle_document_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.delete(url, headers=headers)
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

    def get_vehicle_document(self, token, vehicle_document_id):
        url = f"http://{API_HOST}:{API_PORT}/vehicle_documents/{vehicle_document_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
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

    def get_vehicle_documents(self, token):
        url = f"http://{API_HOST}:{API_PORT}/vehicle_documents/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
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

    def update_vehicle_document(self, token, vehicle_document: dict):
        url = f"http://{API_HOST}:{API_PORT}/vehicle_documents/{vehicle_document.get('id')}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.put(url, json=vehicle_document, headers=headers)
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

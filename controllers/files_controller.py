import requests
from pathlib import Path
from lib.config import API_HOST, API_PORT


class FilesController:

    def delete_file(self, token, subfolder, filename):
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
            return {"error": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_file(self, token, subfolder, filename):
        url = f"http://{API_HOST}:{API_PORT}/files/{filename}?subfolder={subfolder}"
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
            return {"error": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_files(self, token, subfolder):
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
            return {"error": str(e)}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def upload_edit_file(
        self, token, file_path: Path, subfolder: str, name: str, old_name: str
    ):
        url = f"http://{API_HOST}:{API_PORT}/files/edit"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            with open(file_path, "rb") as f:
                files = {"file": (name, f)}
                data = {"subfolder": subfolder}
                old_name = {"old_name": old_name}
                response = requests.post(url, headers=headers, files=files, data=data, old_name=old_name)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:
                return {"error": response.json().get("detail")}
        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}

    def upload_file(self, token, file_path: Path, subfolder: str, name: str):
        url = f"http://{API_HOST}:{API_PORT}/files/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            with open(file_path, "rb") as f:
                files = {"file": (name, f)}
                data = {"subfolder": subfolder}
                response = requests.post(url, headers=headers, files=files, data=data)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:
                return {"error": response.json().get("detail")}
        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}

    def upload_or_replace_file(self, token, file_path: Path, subfolder: str, name: str):
        url = f"http://{API_HOST}:{API_PORT}/files/replace"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            with open(file_path, "rb") as f:
                files = {"file": (name, f)}
                data = {"subfolder": subfolder}
                return requests.post(url, headers=headers, files=files, data=data)
        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}

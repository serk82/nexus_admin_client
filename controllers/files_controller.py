import requests
from pathlib import Path
from lib.config import API_HOST, API_PORT


class FilesController:
    def get_files(self, token, subfolder):
        """
        GET /files/?subfolder=...
        Devuelve lista de nombres de archivo.
        """
        url = f"http://{API_HOST}:{API_PORT}/files/"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"subfolder": subfolder}

        try:
            # IMPORTANTE: params= (query string), no json=
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                # el servidor devuelve detail en json
                return {"error": response.json().get("detail")}
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_file(self, token, subfolder, filename):
        """
        GET /files/{filename}?subfolder=...
        Devuelve bytes (response.content)
        """
        url = f"http://{API_HOST}:{API_PORT}/files/{filename}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"subfolder": subfolder}

        try:
            # mejor construir la URL así y pasar params
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                return response.content
            elif response.status_code == 401:
                return {"error": "No autorizado, token inválido o expirado"}
            elif response.status_code == 404:
                return response.json().get("detail")
            elif response.status_code == 422:
                return {"error": "Datos inválidos enviados"}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_file(self, token, subfolder, filename):
        """
        DELETE /files/?subfolder=...&filename=...
        """
        url = f"http://{API_HOST}:{API_PORT}/files/"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"subfolder": subfolder, "filename": filename}

        try:
            # IMPORTANTE: params= (query string), no json=
            response = requests.delete(url, headers=headers, params=params)

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

        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def upload_edit_file(self, token, file_path: Path, subfolder: str, name: str, old_name: str):
        """
        POST /files/edit  (multipart/form-data)
        No cambia respecto al servidor que hemos hecho.
        """
        url = f"http://{API_HOST}:{API_PORT}/files/edit"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with open(file_path, "rb") as f:
                files = {"file": (name, f)}
                data = {"subfolder": subfolder, "old_name": old_name}
                response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:
                return {"error": response.json().get("detail")}
            else:
                return {"error": f"Error inesperado: {response.status_code}"}

        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}

    def upload_file(self, token, file_path: Path, subfolder: str, name: str):
        """
        POST /files/  (multipart/form-data)
        No cambia.
        """
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
            else:
                return {"error": f"Error inesperado: {response.status_code}"}

        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}

    def upload_or_replace_file(self, token, file_path: Path, subfolder: str, name: str):
        """
        POST /files/replace  (multipart/form-data)
        No cambia.
        """
        url = f"http://{API_HOST}:{API_PORT}/files/replace"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with open(file_path, "rb") as f:
                files = {"file": (name, f)}
                data = {"subfolder": subfolder}
                response = requests.post(url, headers=headers, files=files, data=data)

            # este método antes devolvía el response directamente; lo normal es devolver json si 200
            if response.status_code == 200:
                return response.json()
            else:
                # si hay error, intenta leer detail
                try:
                    return {"error": response.json().get("detail")}
                except Exception:
                    return {"error": f"Error inesperado: {response.status_code}"}

        except Exception as e:
            return {"error": f"No se pudo subir el archivo:\n{e}"}
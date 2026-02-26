import os
import re
import sys
import socket
import platform
import subprocess
import tempfile
import urllib.request


# === VALIDACIONES ==========================================================


def es_ip_valida(ip):
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    partes = ip.split(".")
    return all(0 <= int(parte) <= 255 for parte in partes)


def probar_conexion(ip, puerto=8000, timeout=3):
    try:
        with socket.create_connection((ip, puerto), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False


# === ARCHIVOS Y RUTAS ======================================================


def crear_env(ip):
    with open(".env", "w") as f:
        f.write(f"API_HOST={ip}\nAPI_PORT=8000\n")
    print("✅ Archivo .env creado.")


def crear_carpeta_tmp():
    tmp_path = os.path.abspath("tmp")
    os.makedirs(tmp_path, exist_ok=True)
    print(f"📂 Carpeta temporal creada en {tmp_path}")


def obtener_python_path():
    sistema = platform.system()
    if sistema == "Windows":
        return os.path.abspath("venv")
    else:
        return os.path.abspath("venv/bin/python")


def obtener_pip_path():
    sistema = platform.system()
    if sistema == "Windows":
        return os.path.abspath("venv\\Scripts\\pip.exe")
    else:
        return os.path.abspath("venv/bin/pip")


# === INSTALACIÓN DE DEPENDENCIAS ===========================================


def instalar_pip():
    try:
        url = "https://bootstrap.pypa.io/get-pip.py"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            print("⬇️ Descargando get-pip.py...")
            urllib.request.urlretrieve(url, f.name)
            print("⚙️ Ejecutando get-pip.py...")
            subprocess.check_call([sys.executable, f.name])
        return True
    except Exception as e:
        print(f"❌ Error instalando pip: {e}")
        return False


def instalar_pip_en_venv():
    python_venv = obtener_python_path()
    try:
        url = "https://bootstrap.pypa.io/get-pip.py"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            print("⬇️ Descargando get-pip.py...")
            urllib.request.urlretrieve(url, f.name)
            print("⚙️ Instalando pip dentro del entorno virtual...")
            subprocess.check_call([python_venv, f.name])
        return True
    except Exception as e:
        print(f"❌ Error al instalar pip en el entorno virtual: {e}")
        return False


def instalar_dependencias(requirements="requirements.txt"):
    print("📦 Verificando pip en el entorno virtual...")
    pip_path = obtener_pip_path()

    if not os.path.isfile(pip_path):
        print("❌ pip no encontrado en el entorno virtual. Intentando instalar pip...")
        if not instalar_pip_en_venv():
            raise RuntimeError("No se pudo instalar pip en el entorno virtual.")

    print("📦 Instalando dependencias desde requirements.txt...")
    subprocess.check_call([pip_path, "install", "-r", os.path.abspath(requirements)])
    print("✅ Dependencias instaladas.")


def crear_entorno_virtual(ruta_venv="venv"):
    print("⚙️ Creando entorno virtual...")
    subprocess.check_call([sys.executable, "-m", "venv", ruta_venv])
    print(f"✅ Entorno virtual creado en {ruta_venv}")


def asegurar_dependencias_windows():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("❌ pip no está disponible. Intentando instalar pip...")
        if not instalar_pip():
            return False

    try:
        import winshell
        import win32com.client

        return True
    except ImportError:
        print("🔧 Instalando dependencias para Windows (pywin32, winshell)...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
            )
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pywin32", "winshell"]
            )
            return True
        except Exception as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False


# === ACCESOS DIRECTOS =======================================================


def crear_acceso_directo(nombre, ruta_app, ruta_venv, icono_path=None):
    sistema = platform.system()

    if sistema == "Linux":
        crear_acceso_linux(nombre, ruta_app, ruta_venv, icono_path)
    elif sistema == "Windows":
        if asegurar_dependencias_windows():
            crear_acceso_windows(nombre, ruta_app, ruta_venv, icono_path)
        else:
            print(
                "❌ No se pudieron instalar las dependencias necesarias para Windows."
            )
    else:
        print(f"⚠️ Sistema operativo no soportado: {sistema}")


def crear_acceso_linux(nombre, ruta_app, ruta_venv, icono_path=None):
    apps_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(apps_dir, exist_ok=True)

    launcher = os.path.join(apps_dir, f"{nombre}.desktop")
    contenido = f"""[Desktop Entry]
                Type=Application
                Name={nombre}
                Exec={ruta_venv} {ruta_app}
                Terminal=false
                StartupNotify=true
                StartupWMClass=Nexus-Admin
                Categories=Utility;
                """
    if icono_path:
        contenido += f"Icon={icono_path}\n"

    with open(launcher, "w") as f:
        f.write(contenido)
    os.chmod(launcher, 0o755)
    print(f"📎 Acceso directo creado: {launcher}")


def crear_acceso_windows(nombre, ruta_app, ruta_venv, icono_path=None):
    import winshell
    from pathlib import Path
    from win32com.client import Dispatch

    # Convertir rutas a Path para más legibilidad
    ruta_pythonw = Path(ruta_venv) / "Scripts" / "pythonw.exe"
    ruta_app = Path(ruta_app)
    acceso_path = Path(winshell.desktop()) / f"{nombre}.lnk"

    if not ruta_pythonw.exists():
        raise FileNotFoundError(f"No se encontró pythonw.exe en: {ruta_pythonw}")

    shell = Dispatch("WScript.Shell")
    acceso = shell.CreateShortCut(str(acceso_path))
    acceso.Targetpath = str(ruta_pythonw)
    acceso.Arguments = f'"{ruta_app}"'
    acceso.WorkingDirectory = str(ruta_app.parent)

    if icono_path:
        icono_path = Path(icono_path)
        if icono_path.exists():
            acceso.IconLocation = str(icono_path)

    acceso.save()

    print(f"📎 Acceso directo creado en el escritorio: {acceso_path}")


def crear_acceso_mac(nombre, ruta_app, ruta_venv):
    ruta_command = os.path.expanduser(f"~/Desktop/{nombre}.command")
    with open(ruta_command, "w") as f:
        f.write(f'#!/bin/bash\n"{ruta_venv}" "{ruta_app}"\n')
    os.chmod(ruta_command, 0o755)
    print(f"📎 Script de acceso creado en el escritorio: {ruta_command}")


# === MAIN ===================================================================


def main():
    while True:
        ip = input("Ingrese la IP del servidor: ").strip()
        if not es_ip_valida(ip):
            print("❌ IP inválida. Intente de nuevo.")
            continue

        print("🔍 Probando conexión...")
        if probar_conexion(ip):
            crear_env(ip)
            crear_entorno_virtual()
            crear_carpeta_tmp()
            instalar_dependencias()

            ruta_app = os.path.abspath("app.py")
            ruta_venv = obtener_python_path()
            if platform.system() == "Windows":
                icono_path = os.path.abspath("img/logo.ico")
            else:
                icono_path = os.path.abspath("img/logo.png")

            crear_acceso_directo("Nexus-Admin", ruta_app, ruta_venv, icono_path)

            print("🚀 Instalación completada.")
            break
        else:
            print("❌ No se pudo conectar al servidor. Intente otra IP.")


if __name__ == "__main__":
    main()

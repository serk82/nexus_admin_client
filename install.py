import os
import socket
import re
import subprocess
import sys

def es_ip_valida(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
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

def crear_env(ip):
    with open(".env", "w") as f:
        f.write(f"API_HOST={ip}\nAPI_PORT=8000\n")
    print("✅ Archivo .env creado.")

def crear_entorno_virtual(ruta_venv="venv"):
    print("⚙️ Creando entorno virtual...")
    subprocess.check_call([sys.executable, "-m", "venv", ruta_venv])
    print(f"✅ Entorno virtual creado en {ruta_venv}")

def instalar_dependencias(requirements="requirements.txt"):
    print("📦 Instalando dependencias...")
    pip_path = os.path.abspath("venv/bin/pip")
    requirements_path = os.path.abspath(requirements)
    print(f"Ruta de pip: {pip_path}")
    print(f"Ruta de requirements: {requirements_path}")
    if not os.path.isfile(pip_path):
        raise RuntimeError("No se encontró pip en el entorno virtual")
    subprocess.check_call([pip_path, "install", "-r", requirements_path])
    print("✅ Dependencias instaladas.")

def crear_acceso_directo_menu(nombre, ruta_absoluta_app, ruta_abosluta_venv, icono_path=None):
    apps_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(apps_dir, exist_ok=True)

    ruta_launcher = os.path.join(apps_dir, f"{nombre}.desktop")

    contenido = f"""[Desktop Entry]
                Type=Application
                Name={nombre}
                Exec={ruta_abosluta_venv} {ruta_absoluta_app}
                Terminal=false
                StartupNotify=true
                Categories=Utility;
                """

    if icono_path:
        contenido += f"Icon={icono_path}\n"

    with open(ruta_launcher, "w") as f:
        f.write(contenido)

    os.chmod(ruta_launcher, 0o755)
    print(f"📎 Acceso directo instalado en el menú de aplicaciones: {ruta_launcher}")

def main():
    while True:
        ip = input("Ingrese la IP del servidor: ").strip()
        if not es_ip_valida(ip):
            print("❌ IP inválida. Intente de nuevo.")
            continue

        print("🔍 Probando conexión...")
        if probar_conexion(ip, puerto=8000):
            crear_env(ip)

            # Crear entorno virtual
            crear_entorno_virtual("venv")
            # Instalar dependencias
            instalar_dependencias("requirements.txt")

            ruta_absoluta_app = os.path.abspath("app.py")
            ruta_absoluta_venv = os.path.abspath("venv/bin/python")
            icono_path = os.path.abspath("img/logo.png") if os.path.exists("img/logo.png") else None

            print(f"Ruta absoluta del script: {ruta_absoluta_app}")
            crear_acceso_directo_menu("Nexus-Admin", ruta_absoluta_app, ruta_absoluta_venv, icono_path)

            print("🚀 Instalación completa. Puede usar el acceso directo o ejecutar: python3 app.py")
            break
        else:
            print("❌ No se pudo conectar al servidor. Intente otra IP.")

if __name__ == "__main__":
    main()

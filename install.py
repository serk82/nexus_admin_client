import os
import socket
import re

def es_ip_valida(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    partes = ip.split(".")
    return all(0 <= int(parte) <= 255 for parte in partes)

def probar_conexion(ip, puerto=8000, timeout=3):
    import socket
    try:
        with socket.create_connection((ip, puerto), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def crear_env(ip):
    with open(".env", "w") as f:
        f.write(f"API_HOST={ip}\nAPI_PORT=8000\n")
    print("✅ Archivo .env creado.")

def crear_acceso_directo_linux(nombre, ruta_script, icono_path=None):
    escritorio_path = os.path.expanduser("~/Desktop")
    os.makedirs(escritorio_path, exist_ok=True)

    ruta_launcher = os.path.join(escritorio_path, f"{nombre}.desktop")

    contenido = f"""[Desktop Entry]
Type=Application
Name={nombre}
Exec=python3 {ruta_script}
Terminal=false
"""

    if icono_path:
        contenido += f"Icon={icono_path}\n"

    with open(ruta_launcher, "w") as f:
        f.write(contenido)

    os.chmod(ruta_launcher, 0o755)
    print(f"📎 Acceso directo creado: {ruta_launcher}")

def main():
    while True:
        ip = input("Ingrese la IP del servidor: ").strip()
        if not es_ip_valida(ip):
            print("❌ IP inválida. Intente de nuevo.")
            continue

        print("🔍 Probando conexión...")
        if probar_conexion(ip, puerto=8000):
            crear_env(ip)

            # ruta_absoluta = os.path.abspath("app.py")
            # crear_acceso_directo_linux("MiAplicacionPyQt6", ruta_absoluta)
            print("🚀 Instalación completa. Puede usar el acceso directo o ejecutar: python3 app.py")
            break
        else:
            print("❌ No se pudo conectar al servidor. Intente otra IP.")

if __name__ == "__main__":
    main()

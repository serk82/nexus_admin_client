# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde .env

API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")
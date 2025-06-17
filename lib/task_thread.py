import traceback
from PyQt6.QtCore import QThread, pyqtSignal


class TaskThread(QThread):
    show_message_info = pyqtSignal(str, str)
    show_message_response = pyqtSignal(str, str)
    response_message = pyqtSignal(bool)
    progress = pyqtSignal(int)  # Señal para actualizar el progreso
    total_progress = pyqtSignal(int)  # Señal para actualizar el progreso total
    messages = pyqtSignal(str)  # Señal para mostrar mensajes
    working = pyqtSignal(str)  # Señal para mostrar el mensaje de trabajo
    finished = pyqtSignal()  # Señal para indicar que terminó el proceso
    error = pyqtSignal(str, str)  # Señal para capturar errores

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.run = catch_exceptions(self.error)(self.run)

    def run(self):
        self.task()
        self.finished.emit()


import traceback
from functools import wraps


def catch_exceptions(error_signal):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tb_str = traceback.format_exc()
                error_signal.emit(str(e), tb_str)

        return wrapper

    return decorator


from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel
from PyQt6.QtGui import QMovie


class LoadingDialog(QDialog):
    # Ventana modal con círculo giratorio
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cargando...")
        self.setFixedSize(100, 100)
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(100, 100)

        BASE_DIR = Path(__file__).resolve().parents[1]
        img_path = BASE_DIR / "lib" / "Spinner.gif"
        self.movie = QMovie(str(img_path))
        self.movie.setScaledSize(self.label.size())  # Ajustar tamaño del GIF
        self.label.setMovie(self.movie)
        self.movie.start()

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 200); border-radius: 10px;"
        )

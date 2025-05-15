from PyQt6.QtCore import QThread, pyqtSignal


class TaskThread(QThread):
    finished = pyqtSignal()  # Señal para indicar que terminó el proceso
    error = pyqtSignal(str)  # Señal para capturar errores

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        try:
            self.task()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


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

        self.movie = QMovie("lib/Spinner.gif")
        self.movie.setScaledSize(self.label.sizeHint())  # Ajustar tamaño del GIF
        self.label.setMovie(self.movie)
        self.movie.start()

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 200); border-radius: 10px;"
        )

import sys
import os
import signal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
import subprocess
import math

signal.signal(signal.SIGINT, signal.SIG_DFL)

OVERLAY_FOLDER = os.path.join(os.path.dirname(__file__), "../overlays")
GIF_FILE = os.path.join(OVERLAY_FOLDER, "snake.gif")
KOJIMA_IMG = os.path.join(OVERLAY_FOLDER, "kojima.jpg")
AUDIO_FILE = os.path.join(OVERLAY_FOLDER, "audio/invisible_clip.mp4")
SCREENSHOT_IMG = "/tmp/screen.png"

class KojimaOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool) # type: ignore
        self.setAttribute(Qt.WA_TranslucentBackground) # type: ignore

        self.bg = QPixmap(SCREENSHOT_IMG)
        if self.bg.isNull():
            raise FileNotFoundError(f"Failed to load {SCREENSHOT_IMG}")

        # Snake GIF setup
        self.gif_label = QLabel(self)
        self.movie = QMovie(GIF_FILE)
        if not self.movie.isValid():
            raise FileNotFoundError(f"Failed to load or parse {GIF_FILE}")
        self.movie.setSpeed(60)
        self.gif_label.setMovie(self.movie)
        self.gif_label.setScaledContents(True)
        self.gif_label.setGeometry(100, 512, 500, 500)
        self.gif_label.setVisible(True)

        # Snake fade effect
        self.snake_effect = QGraphicsOpacityEffect()
        self.gif_label.setGraphicsEffect(self.snake_effect)
        self.snake_anim = QPropertyAnimation(self.snake_effect, b"opacity")
        self.snake_anim.setDuration(6000)
        self.snake_anim.setStartValue(0)
        self.snake_anim.setEndValue(1)

        # Kojima fullscreen overlay
        self.kojima_full = QLabel(self)
        self.kojima_full.setScaledContents(True)
        self.kojima_full.setPixmap(QPixmap(KOJIMA_IMG))
        self.kojima_effect = QGraphicsOpacityEffect()
        self.kojima_effect.setOpacity(0)
        self.kojima_full.setGraphicsEffect(self.kojima_effect)
        self.kojima_anim = QPropertyAnimation(self.kojima_effect, b"opacity")
        self.kojima_anim.setDuration(19000)
        self.kojima_anim.setStartValue(0)
        self.kojima_anim.setEndValue(0.8)

        self.arrow_start = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else None

        self.showFullScreen()
        self.start_cinematic()
        QTimer.singleShot(25000, self.cleanup)

    def start_cinematic(self):
        self.movie.start()
        self.snake_anim.start()

        QTimer.singleShot(4000, self.kojima_anim.start)
        self.play_audio()

    def paintEvent(self, event): # type: ignore
        painter = QPainter(self)
        if not self.bg.isNull():
            painter.drawPixmap(self.rect(), self.bg)
        if self.arrow_start:
            # End = center of snake gif
            end_x = self.gif_label.x() + self.gif_label.width() // 2
            end_y = self.gif_label.y() + self.gif_label.height() // 2

            painter.setPen(QColor(243, 139, 168))
            painter.setBrush(Qt.NoBrush) # type: ignore
            painter.setRenderHint(QPainter.Antialiasing)
            pen = painter.pen()
            pen.setWidth(6)
            painter.setPen(pen)
            painter.drawLine(self.arrow_start[0], self.arrow_start[1], end_x, end_y)

            self.draw_arrowhead(painter, self.arrow_start[0], self.arrow_start[1], end_x, end_y)


    def resizeEvent(self, event): # type: ignore
        self.kojima_full.setGeometry(self.rect())
        scaled_pixmap = QPixmap(KOJIMA_IMG).scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation # type: ignore
        )
        self.kojima_full.setPixmap(scaled_pixmap)

    def play_audio(self):
        subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", AUDIO_FILE])

    def cleanup(self):
        subprocess.Popen(["pkill", "-n", "ffplay"])
        self.close()

    def draw_arrowhead(self, painter, x1, y1, x2, y2):
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 20
        p1 = x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6)
        p2 = x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6)

        painter.drawLine(x2, y2, int(p1[0]), int(p1[1]))
        painter.drawLine(x2, y2, int(p2[0]), int(p2[1]))

app = QApplication(sys.argv)
window = KojimaOverlay()
window.show()
sys.exit(app.exec_())
"""Чистый PyQt6-код: на Mavericks идёт через шим, на новых системах — на настоящем PyQt6."""
import sys

from PyQt6.QtCore import QT_VERSION_STR, Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtWidgets import (QApplication, QCheckBox, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt6 demo')

        self.label = QLabel('Привет, PyQt6!')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)

        check = QCheckBox('Галочка')
        check.stateChanged.connect(self.on_check)
        button = QPushButton('Нажми')
        button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        for w in (self.label, check, button):
            layout.addWidget(w)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        quit_action = QAction('Выход', self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        self.menuBar().addMenu('Файл').addAction(quit_action)
        self.statusBar().showMessage(f'Qt {QT_VERSION_STR}')

    def on_check(self, state):
        # сигнал отдаёт int, а enum в PyQt6 — не int, поэтому .value
        self.label.setText('Галочка стоит' if state == Qt.CheckState.Checked.value else 'Галочки нет')

    def on_click(self):
        answer = QMessageBox.question(self, 'Вопрос', 'Работает?')
        if answer == QMessageBox.StandardButton.Yes:
            self.label.setText('Отлично!')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            p = event.position().toPoint()
            self.statusBar().showMessage(f'Клик: {p.x()}, {p.y()}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.resize(360, 220)
    window.show()
    if '--test' in sys.argv:
        QTimer.singleShot(300, app.quit)
    sys.exit(app.exec())

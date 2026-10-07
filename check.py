"""Самопроверка: python3.12 check.py. Тот же файл проходит и на настоящем PyQt6."""
import io
import os
import sys
import tempfile

import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets, sip, uic
from PyQt6.QtCore import QEvent, QPointF, QRegularExpression, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QFont, QFontMetrics, QImage, QMouseEvent, QPixmap, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QDialog, QFrame, QPlainTextEdit, QWidget

UI = b'''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <layout class="QVBoxLayout" name="lay">
   <item>
    <widget class="QLabel" name="label">
     <property name="text"><string>a::b::c</string></property>
     <property name="alignment"><set>Qt::AlignmentFlag::AlignRight|Qt::AlignmentFlag::AlignVCenter</set></property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="btn">
     <property name="icon">
      <iconset>
       <normaloff>i.png</normaloff>i.png</iconset>
     </property>
    </widget>
   </item>
   <item>
    <widget class="QFrame" name="frame">
     <property name="frameShape"><enum>QFrame::Shape::Box</enum></property>
    </widget>
   </item>
  </layout>
 </widget>
</ui>'''


def ui_ok(form):
    return (form.label.alignment() == Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            and form.label.text() == 'a::b::c' and form.frame.frameShape() == QFrame.Shape.Box)


def load_ui():
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, 'form.ui')
    with open(path, 'wb') as f:
        f.write(UI)
    pixmap = QPixmap(4, 4)
    pixmap.fill()
    pixmap.save(os.path.join(folder, 'i.png'))
    w = QWidget()
    uic.loadUi(path, w)
    form_class, base = uic.loadUiType(path)
    return ui_ok(w) and ui_ok(uic.loadUi(io.BytesIO(UI))) and not w.btn.icon().isNull() and base is QWidget


def mouse():
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(5, 7), Qt.MouseButton.LeftButton,
                     Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    return ev.position() == QPointF(5, 7) and ev.globalPosition() is not None


def tab_stop():
    edit = QPlainTextEdit()
    edit.setTabStopDistance(33.0)
    return edit.tabStopDistance() == 33


def filter_re():
    model = QStandardItemModel()
    for text in ('Alpha', 'beta', 'Gamma'):
        model.appendRow(QStandardItem(text))
    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    proxy.setFilterRegularExpression(
        QRegularExpression('^a', QRegularExpression.PatternOption.CaseInsensitiveOption))
    return proxy.rowCount() == 1


CHECKS = {
    'enum: .value / .name': lambda: Qt.CheckState.Checked.value == 2 and Qt.CheckState.Checked.name == 'Checked',
    'флаги: .value': lambda: (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop).value == 0x21,
    'enum уровня модуля': lambda: QtCore.QtMsgType.QtDebugMsg.name == 'QtDebugMsg',
    'QAction в QtGui, а не в QtWidgets': lambda: hasattr(QtGui, 'QAction') and not hasattr(QtWidgets, 'QAction'),
    'exec()': lambda: hasattr(QDialog, 'exec') and hasattr(QApplication, 'exec'),
    'event.position()': mouse,
    'horizontalAdvance()': lambda: QFontMetrics(QFont()).horizontalAdvance('abc') > 0,
    'QImage.sizeInBytes()': lambda: QImage(4, 4, QImage.Format.Format_RGB32).sizeInBytes() == 64,
    'setTabStopDistance()': tab_stop,
    'setFilterRegularExpression()': filter_re,
    'QWidget.screen()': lambda: QWidget().screen() is not None,
    'PyQt6.sip': lambda: callable(sip.isdeleted),
    'PyQt6.QtSvgWidgets': lambda: __import__('PyQt6.QtSvgWidgets', fromlist=['QSvgWidget']).QSvgWidget is not None,
    'uic.loadUi (.ui из Designer 6)': load_ui,
}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print('Python %s | Qt %s | %s' % (sys.version.split()[0], QtCore.QT_VERSION_STR, 'шим поверх PyQt5 '
          + QtCore.PYQT_VERSION_STR if hasattr(PyQt6, '_Finder') else 'настоящий PyQt6'))
    bad = 0
    for name, check in CHECKS.items():
        try:
            ok, why = check(), ''
        except Exception as e:  # noqa: BLE001
            ok, why = False, '  (%s: %s)' % (type(e).__name__, e)
        bad += not ok
        print('  %s  %s%s' % ('ok  ' if ok else 'FAIL', name, why))
    print('Всё работает.' if not bad else 'Не прошло: %d — пришли этот вывод.' % bad)
    sys.exit(bool(bad))

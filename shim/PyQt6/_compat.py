"""Ядро шима: подгоняет классы PyQt5 под API PyQt6. Добавляет только то, чего нет."""
try:
    from PyQt5 import sip
except ImportError:  # PyQt5 < 5.11
    import sip

# Есть в PyQt5, но нет в PyQt6 (или переехало) — прячем, чтобы код оставался валидным PyQt6
_GONE = {
    'QtCore': ('QRegExp', 'QTextCodec', 'QTextDecoder', 'QTextEncoder'),
    'QtGui': ('QRegExpValidator', 'QMatrix'),
    'QtWidgets': ('QAction', 'QActionGroup', 'QShortcut', 'QUndoCommand', 'QUndoGroup', 'QUndoStack',
                  'QFileSystemModel', 'QDesktopWidget', 'QDirModel', 'QOpenGLWidget', 'qApp'),
    'QtSvg': ('QSvgWidget', 'QGraphicsSvgItem'),
}


def _tab_stop(self, distance):
    self.setTabStopWidth(round(distance))


def _filter_re(self, rx):
    from PyQt5.QtCore import QRegExp, QRegularExpression, Qt
    cs = self.filterCaseSensitivity()
    if not isinstance(rx, str):
        if rx.patternOptions() & QRegularExpression.CaseInsensitiveOption:
            cs = Qt.CaseInsensitive
        rx = rx.pattern()
    self.setFilterRegExp(QRegExp(rx, cs))


def _screen(self):
    from PyQt5.QtGui import QGuiApplication
    handle = self.window().windowHandle()
    return handle.screen() if handle else QGuiApplication.primaryScreen()


_POS = {'position': 'localPos', 'scenePosition': 'windowPos', 'globalPosition': 'screenPos'}
_POSF = {'position': 'posF', 'globalPosition': 'globalPosF'}
_TAB = {'setTabStopDistance': _tab_stop, 'tabStopDistance': 'tabStopWidth'}
# Класс -> {имя из Qt6: старое имя из Qt5 или функция}
_NEW = {
    'QMouseEvent': _POS, 'QEnterEvent': _POS, 'QWheelEvent': _POSF, 'QTabletEvent': _POSF,
    'QHoverEvent': {'position': 'posF'}, 'QDropEvent': {'position': 'posF'},
    'QFontMetrics': {'horizontalAdvance': 'width'}, 'QFontMetricsF': {'horizontalAdvance': 'width'},
    'QImage': {'sizeInBytes': 'byteCount'},
    'QTextEdit': _TAB, 'QPlainTextEdit': _TAB,
    'QSortFilterProxyModel': {'setFilterRegularExpression': _filter_re},
    'QWidget': {'screen': _screen},
}

_seen = set()
_names = {}  # тип enum -> {значение: имя}


def _enums(ns):
    """Qt.AlignCenter -> ещё и Qt.AlignmentFlag.AlignCenter; у enum-ов появляются .value и .name."""
    for key, val in list(ns.items()):
        t = type(val)
        if key.startswith('_') or not isinstance(val, int) or t in (int, bool):
            continue
        if t not in _names:
            names = _names[t] = {}
            if not hasattr(t, 'value'):
                t.value = property(int)
            if not hasattr(t, 'name'):
                t.name = property(lambda self, n=names: n.get(int(self)))
            flags = type(val | val)  # Qt.AlignmentFlag -> Qt.Alignment и т.п.
            if flags not in (t, int) and not hasattr(flags, 'value'):
                flags.value = property(int)
        _names[t].setdefault(int(val), key)
        if not hasattr(t, key):
            setattr(t, key, val)


def _patch(cls):
    if cls in _seen or not isinstance(cls, sip.wrappertype):
        return
    _seen.add(cls)
    d = vars(cls)  # заодно заставляет sip заполнить «ленивые» атрибуты
    _enums(d)
    for name in ('exec', 'print'):  # exec_() -> exec() для старых PyQt5
        if name + '_' in d and name not in d:
            setattr(cls, name, d[name + '_'])
    for new, old in _NEW.get(cls.__name__, {}).items():
        if not hasattr(cls, new) and (callable(old) or hasattr(cls, old)):
            # getattr(cls, old) у sip — уже не дескриптор, поэтому через self
            setattr(cls, new, old if callable(old) else (lambda self, *a, _o=old: getattr(self, _o)(*a)))
    for v in list(d.values()):
        if isinstance(v, type):
            _patch(v)  # вложенные классы
    for base in cls.__mro__[1:]:
        _patch(base)


def fix(ns):
    """Каждый модуль шима вызывает это со своим globals()."""
    for name in _GONE.get(ns['__name__'].rpartition('.')[2], ()):
        ns.pop(name, None)
    _enums(ns)  # enum-ы уровня модуля (QtCore.QtMsgType и т.п.)
    for v in list(ns.values()):
        if isinstance(v, type):
            _patch(v)

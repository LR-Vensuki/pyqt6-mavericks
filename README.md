# PyQt6 на macOS 10.9 Mavericks

Qt6 требует macOS 10.14+, поэтому настоящий PyQt6 на Mavericks не запустится.
`shim/PyQt6` — пакет с именем `PyQt6`, который внутри работает на PyQt5 5.8.2 (Qt 5.8 — последний Qt для 10.9).
Пишешь обычный PyQt6-код, а у преподавателя он без правок запускается на настоящем PyQt6.
В комплекте есть патч для PyCharm 2017.3.7 — последней версии под 10.9 — чтобы он работал с Python 3.12.

## Установка с нуля

Все команды выполняй в Терминале.

```sh
cd ~
# 1. Python 3.12.5 — последний установщик python.org для 10.9
#    (если curl ругается на SSL, скачай файл на другом компьютере)
curl -fLo python.pkg https://www.python.org/ftp/python/3.12.5/python-3.12.5-macos11.pkg
sudo installer -pkg python.pkg -target /
"/Applications/Python 3.12/Install Certificates.command"

# 2. Этот репозиторий (дальше всё качает сам Python — у него свежий OpenSSL)
python3.12 -c "import urllib.request as u; u.urlretrieve('https://github.com/LR-Vensuki/pyqt6-mavericks/archive/refs/heads/main.zip', 'pyqt6-mavericks.zip')"
unzip -q pyqt6-mavericks.zip && mv pyqt6-mavericks-main pyqt6-mavericks
cd ~/pyqt6-mavericks

# 3. PyQt5 5.8.2 + PyQt5-sip, подключение шима и проверка
python3.12 install.py
python3.12 check.py      # в конце должно быть «Всё работает.»
python3.12 demo.py       # окно, внизу «Qt 5.8.0»

# 4. PyCharm Community 2017.3.7 и патч под Python 3.12
python3.12 -c "import urllib.request as u; u.urlretrieve('https://download.jetbrains.com/python/pycharm-community-2017.3.7.dmg', 'pycharm.dmg')"
hdiutil attach pycharm.dmg -nobrowse -mountpoint /Volumes/PyCharmCE
cp -R "/Volumes/PyCharmCE/PyCharm CE.app" /Applications/
hdiutil detach /Volumes/PyCharmCE && rm pycharm.dmg
python3.12 pycharm_fix.py "/Applications/PyCharm CE.app"
open "/Applications/PyCharm CE.app"
```

Если скачал PyCharm через браузер, перед `pycharm_fix.py` запусти его один раз и закрой: иначе Gatekeeper
может счесть изменённую программу повреждённой. При скачивании командой выше это не нужно.

## Настройка PyCharm

1. Create New Project → Project Interpreter → **Existing interpreter** → «…» → **System Interpreter**.
2. Путь: `/Users/<имя>/pyqt6-mavericks/ide/python`. В окне выбора файла нажми ⌘⇧G.
3. Не создавай Virtualenv: в нём не будет ни PyQt5, ни шима.

`ide/python` — обёртка над Python 3.12, её создаёт `pycharm_fix.py`. PyCharm 2017.3 читает «3.12» как «3.1»
и подчёркивает даже f-строки, а обёртка говорит ему «3.6».

`pycharm_fix.py` чинит служебные скрипты PyCharm: без него на Python 3.12 падают отладчик, консоль и список пакетов.
Оригиналы остаются рядом как `*.py.orig`. Ещё он ставит `setuptools<81` и `zombie-imp`.

В `shim/PyQt6` лежат `.pyi`-стабы настоящего PyQt6 6.11, поэтому PyCharm подсказывает API именно PyQt6.
Он же подчеркнёт то, чего в PyQt6 нет: `Qt.AlignCenter`, `exec_()`, `QtWidgets.QAction`.
Синтаксис новее 3.6 (`:=`, `match`) он подчеркнёт красным, но код всё равно запускается.

## Правила для кода

- Импорты только из `PyQt6`; `QAction`, `QShortcut`, `QActionGroup`, `QUndo*` и `QFileSystemModel` — из `QtGui`.
- Enum-ы только полные: `Qt.AlignmentFlag.AlignCenter`; `app.exec()`, а не `exec_()`.
- Сигналы отдают `int`, а enum в PyQt6 — не `int`. Пиши `state == Qt.CheckState.Checked.value`.
  Вариант `== Qt.CheckState.Checked` здесь сработает, а в PyQt6 — нет.
- То, чего нет в Qt 5.8, здесь не заработает: новые классы Qt6, `QtMultimedia` в стиле Qt6 с `QAudioOutput`.
- Перед сдачей лучше хоть раз запустить код на настоящем PyQt6.

## Что делает шим

- Классы, переехавшие в Qt6, берутся из `QtGui`, из `QtWidgets` они убраны.
- Enum-ы как в PyQt6: `.value`, `.name`, полные имена; есть `exec()`.
- Методы с именами из Qt6: `event.position()` / `globalPosition()`, `horizontalAdvance()`, `QImage.sizeInBytes()`,
  `setTabStopDistance()`, `setFilterRegularExpression()`, `QWidget.screen()`.
- `uic.loadUi()` понимает `.ui` из Qt Designer 6.
- `PyQt6.QtSvgWidgets`, `PyQt6.QtOpenGLWidgets` и любые другие `PyQt6.QtXxx` берутся из PyQt5.
- `shim/sip.py` — мост, через который PyQt5 5.8 работает на новом Python.

## Другие библиотеки

Чистые Python-библиотеки работают как есть. Скомпилированные ставь с `--prefer-binary`:
`python3.12 -m pip install --prefer-binary numpy`. Тогда pip возьмёт последнюю версию с готовой сборкой под 10.9
(для numpy это 2.1.1), а не будет собирать новую из исходников.
Не ставь PyQt5 через `pip install PyQt5`: pip выберет версию с Qt, который на 10.9 падает.

## Если что-то не так

Пришли вывод `python3.12 check.py`. Отключить шим: `python3.12 install.py --uninstall`.
Если перенесёшь папку, снова запусти `install.py` и `pycharm_fix.py`.

## Лицензия

GPLv3 (см. `LICENSE`). Файлы `shim/PyQt6/*.pyi` взяты из PyQt6 (Riverbank Computing, GPLv3).

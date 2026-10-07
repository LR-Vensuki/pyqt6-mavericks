"""Ставит PyQt5 под Mavericks и подключает шим PyQt6 к ЭТОМУ Python.

    python3.12 install.py               поставить
    python3.12 install.py --uninstall   отключить шим
"""
import importlib.metadata
import importlib.util
import os
import site
import subprocess
import sys
import sysconfig

SHIM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shim')
user = sys.prefix == sys.base_prefix and site.ENABLE_USER_SITE
target = site.getusersitepackages() if user else sysconfig.get_paths()['purelib']
pth = os.path.join(target, 'pyqt6_shim.pth')


def version(dist):
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return None


if '--uninstall' in sys.argv:
    if os.path.exists(pth):
        os.remove(pth)
    print('Шим отключён.')
    sys.exit()

spec = importlib.util.find_spec('PyQt6')
if spec and not (spec.origin or '').startswith(SHIM):
    sys.exit('Тут уже есть настоящий PyQt6 (%s) — шим не нужен.' % spec.origin)

# PyQt5 5.8.2 — последний, чей Qt (5.8) работает на 10.9; PyQt5-sip даёт ему sip под новый Python
missing = [pkg for pkg, ok in (('PyQt5-sip', version('PyQt5-sip')), ('PyQt5==5.8.2', version('PyQt5') == '5.8.2'))
           if not ok]
if missing:
    print('Ставлю:', ' '.join(missing))
    cmd = [sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', '--no-deps']
    if subprocess.call(cmd + (['--user'] if user else []) + missing):
        sys.exit('pip не смог поставить пакеты — ошибка выше.')

os.makedirs(target, exist_ok=True)
with open(pth, 'w', encoding='utf-8') as f:
    f.write(SHIM + '\n')
print('Готово. Проверка:', sys.executable, os.path.join(os.path.dirname(SHIM), 'check.py'))

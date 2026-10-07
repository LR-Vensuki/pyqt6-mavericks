"""Готовит старый PyCharm (2017.3 — последний для 10.9) к Python 3.12.

    python3.12 pycharm_fix.py "/Applications/PyCharm CE.app"

1. Чинит служебные скрипты PyCharm (отладчик, скелеты, консоль): они зовут API,
   убранные из Python 3.9–3.12. Оригиналы сохраняются рядом как *.py.orig.
2. Ставит setuptools<81 и zombie-imp: менеджеру пакетов PyCharm нужны pkg_resources и imp.
3. Делает обёртку ide/python: PyCharm 2017.3 читает «3.12» как «3.1» и красит f-строки
   ошибками, а обёртка отвечает ему на `python -V`, что это 3.6 (новее он не знает).
"""
import os
import re
import shutil
import site
import subprocess
import sys

FIXES = [  # регулярка -> замена
    (r'\.isAlive\(\)', '.is_alive()'),  # убрано в 3.9 — из-за этого молчит отладчик
    (r'inspect\.getargspec\(([^()]*)\)', r'inspect.getfullargspec(\1)[:4]'),  # убрано в 3.11
    (r'inspect\.formatargspec\(\*spec_info\)', 'str(inspect.signature(fob))'),  # убрано в 3.11
    (r'Regex\("\.\*\(\?s\)"\)', 'Regex("(?s).*")'),  # с 3.11 флаги (?s) только в начале
]

if len(sys.argv) != 2:
    sys.exit(__doc__)
app = sys.argv[1]
helpers = os.path.join(app, 'Contents', 'helpers')
if not os.path.isdir(helpers):
    helpers = os.path.join(app, 'helpers')
if not os.path.isdir(helpers):
    sys.exit('Не нашёл папку helpers в %s' % app)

patched = 0
for root, _, files in os.walk(helpers):
    for name in files:
        if not name.endswith('.py'):
            continue
        path = os.path.join(root, name)
        with open(path, encoding='utf-8', errors='surrogateescape') as f:
            src = f.read()
        new = src
        for rx, rep in FIXES:
            new = re.sub(rx, rep, new)
        if new != src:
            if not os.path.exists(path + '.orig'):
                shutil.copy2(path, path + '.orig')
            with open(path, 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(new)
            patched += 1
print('Исправлено файлов в helpers:', patched)

user = sys.prefix == sys.base_prefix and site.ENABLE_USER_SITE
cmd = [sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'setuptools<81', 'zombie-imp']
if subprocess.call(cmd + (['--user'] if user else [])):
    sys.exit('pip не смог поставить setuptools/zombie-imp — ошибка выше.')

wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ide', 'python')
os.makedirs(os.path.dirname(wrapper), exist_ok=True)
with open(wrapper, 'w') as f:
    f.write('#!/bin/sh\n'
            '# Для PyCharm 2017.3: на `python -V` говорим 3.6, иначе он считает 3.12 за 3.1\n'
            'case "$1" in -V|--version) echo "Python 3.6.99"; exit 0;; esac\n'
            'exec "%s" "$@"\n' % sys.executable)
os.chmod(wrapper, 0o755)
print('Интерпретатор для PyCharm:', wrapper)

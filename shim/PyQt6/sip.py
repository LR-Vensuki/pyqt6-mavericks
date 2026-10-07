try:
    from PyQt5.sip import *  # noqa: F401,F403
except ImportError:  # PyQt5 < 5.11
    from sip import *  # noqa: F401,F403

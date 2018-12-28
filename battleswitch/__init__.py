import enum
import threading

from flask import Flask

__all__ = ['CellState', 'GameState', 'StateLock', 'app', 'ifAdminStatus', 'ifOperStatus']

StateLock = threading.RLock()


class ifAdminStatus(enum.Enum):
    up = 1
    down = 2
    testing = 3

ifAdminStatus.oid = (1, 3, 6, 1, 2, 1, 2, 2, 1, 7)


class ifOperStatus(enum.Enum):
    up = 1
    down = 2
    testing = 3

ifOperStatus.oid = (1, 3, 6, 1, 2, 1, 2, 2, 1, 8)


class GameState(enum.Enum):
    PREPARING = 0
    RUNNING = 1
    OVER = 2


class CellState(enum.Enum):
    EMPTY = (0, ifAdminStatus.down)
    PRESENT = (1, ifAdminStatus.up)
    HIT = (2, ifAdminStatus.up)

    def __new__(cls, value, admin_status):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.admin_status = admin_status
        return obj


app = Flask(__package__)

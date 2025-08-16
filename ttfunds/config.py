import os

CONFIG = {
    "db_path": os.path.join(os.path.dirname(__file__), "funds.db"),
    "proxy_api": None,
    "timeout": 10,
    "retries": 3,
    "max_workers_realtime": 5,
    "max_workers_history": 3,
}


def configure(**kwargs):
    CONFIG.update(kwargs)
    return CONFIG
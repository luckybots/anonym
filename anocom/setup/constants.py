from pathlib import Path
import sys

LOG_FORMAT = '%(module)-12s: %(asctime)s %(levelname)s %(message)s'

APP_DIR = Path(sys.modules['__main__'].__file__).parent.parent

UPDATE_SECONDS = 1
RESTART_SECONDS = 10

BOT_LOOK_BACK_DAYS = 1
LONG_POLLING_TIMEOUT = 1

MESSAGES_LOG_PREFIX = 'messages'
MESSAGES_LOG_CHAT_TYPES = ['private']

def data_dir():
    return APP_DIR/'data'


def state_dir():
    return data_dir()/'state'


def config_path():
    return data_dir()/'config.json'


def config_example_path():
    return data_dir()/'config_example.json'


def log_dir():
    return data_dir()/'logs'


def csv_log_dir():
    return data_dir()/'csv_logs'


def messages_log_dir():
    return csv_log_dir()/'messages'


def enabled_chats_state_path():
    return state_dir()/'enabled_chats.json'

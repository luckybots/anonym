from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = '%(module)-12s: %(asctime)s %(levelname)s %(message)s'

APP_DIR = Path('./')

RESTART_TIMEOUT = 10 # seconds

def data_dir():
    return APP_DIR/'data'

def config_path():
    return data_dir()/'config.json'

def log_dir():
    return APP_DIR/'logs'



# Build default_logger
if True:
    default_logger = logging.getLogger('default_logger')
    default_logger.setLevel(logging.DEBUG)
    default_log_formatter = logging.Formatter(LOG_FORMAT)

    log_dir().mkdir(exist_ok=True, parents=True)
    log_file_handler = TimedRotatingFileHandler(log_dir()/"log.log",
                                                when="midnight",
                                                backupCount=30)
    log_file_handler.setFormatter(default_log_formatter)
    log_file_handler.setLevel(logging.INFO)
    default_logger.addHandler(log_file_handler)


    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.INFO)
    log_console_handler.setFormatter(default_log_formatter)
    default_logger.addHandler(log_console_handler)




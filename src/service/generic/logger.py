import logging
import sys
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter
from pythonjsonlogger.json import JsonFormatter

from src.config import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


# region formatters
json_file_formatter = JsonFormatter(  # Если передать словарь, то добавит поля
    "%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s"
)
verbose_formatter = ColoredFormatter( # Форматер для вывода в консоль с цветом
    "%(log_color)s%(levelname)-9s %(asctime)s %(module)s:%(funcName)s\n"
    "%(message)s\n",
    datefmt='%H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)
# endregion

# region Менее подробный файл для всей информации
json_handler = RotatingFileHandler(
    f"{settings.LOG_LOCATION}/log.json",
    encoding="utf-8",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
json_handler.setLevel(logging.INFO)
json_handler.setFormatter(json_file_formatter)
logger.addHandler(json_handler)
# endregion

# region Обычный вывод для debug-а при разработке
verbose_output = logging.StreamHandler(sys.stdout)
verbose_output.setLevel(logging.DEBUG)
verbose_output.setFormatter(verbose_formatter)
logger.addHandler(verbose_output)
# endregion

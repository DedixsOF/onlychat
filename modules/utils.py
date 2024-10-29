import configparser
import logging
import os

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename='logs/server_logs.txt', level=logging.INFO, filemode='a',
                    format = "%(asctime)s %(levelname)s %(message)s", datefmt = "%a %d %b %Y %H:%M:%S")
    return logging.getLogger()

class Utils:
    @staticmethod
    def setup_chat_logger(chat_id):
        # Убедитесь, что директория для логов существует
        if not os.path.exists('logs/chat_logs'):
            os.makedirs('logs/chat_logs')
        # Создание логгера
        logger = logging.getLogger(f'chat_{chat_id}')
        logger.setLevel(logging.INFO)
        # Создание обработчика для записи в файл
        handler = logging.FileHandler(f'logs/chat_logs/chat_{chat_id}.log', mode ='a')
        handler.setLevel(logging.INFO)
        # Создание форматтера и добавление его в обработчик
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt = "%a %d %b %Y %H:%M:%S")
        handler.setFormatter(formatter)
        # Добавление обработчика к логгеру
        logger.addHandler(handler)

        return logger
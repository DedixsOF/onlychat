import configparser
import logging

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def setup_logging():
    logging.basicConfig(filename='logs/chat_logs.txt', level=logging.INFO, filemode='a',
                    format = "%(asctime)s %(levelname)s %(message)s", datefmt = "%a %d %b %Y %H:%M:%S")
    return logging.getLogger()
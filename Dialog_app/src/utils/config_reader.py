# config_reader.py
import configparser
import os

def read_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, '..', '..', 'config.ini')  # Modify this line
    config.read(config_path)
    return config

# config_reader.py
import configparser
import os

def read_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = '../../config.ini'
    print(config_path)
    config.read(config_path)
    return config

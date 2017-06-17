import json
import logging
import os
from pprint import pprint
from singleton import Singleton
import namedtupled


@Singleton
class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def info(self, msg):
        logging.info(msg)

    def debug(self, msg):
        logging.debug(msg)

    def error(self, msg):
        logging.error(msg)


logger = Logger.instance()

CONFIGURATION_FILENAME = 'conf.json'


def filename_to_named_tuple(filename):
    with open(filename) as data_file:
        c_ = json.load(data_file)
        pprint(c_)
        return namedtupled.map(c_)


def load_constants():
    c_ = None
    try:
        c_ = filename_to_named_tuple(CONFIGURATION_FILENAME)
    except FileNotFoundError as e:
        logger.error(e)
        logger.error('Please execute this command: cp conf.json.example conf.json')
    return c_


c = load_constants()
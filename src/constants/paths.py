from os.path import join, expanduser

from src.constants.application import Application


class Paths(object):
    CONFIGURATION_DIRECTORY = join(expanduser('~'), f'.{Application.NAME}')
    CONFIGURATION_FILE_NAME = 'config.json'
    CONFIGURATION_FILE_PATH = join(CONFIGURATION_DIRECTORY, CONFIGURATION_FILE_NAME)
    DEFAULT_REMOTE_DIRECTORY_FOR_SYNCHRONIZATION = '~/sync'

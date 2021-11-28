from os import mkdir
from getpass import getpass
from os.path import isdir, isfile, expanduser
from json import dump, load, JSONDecodeError

from src.utils.decorators.singleton import singleton
from src.helpers.state import state
from src.constants.paths import Paths
from src.models.connection_credentials import ConnectionCredentials
from src.services.logger_service import logger


@singleton
class ConfigService(ConnectionCredentials):
    CONFIGURATION_DIRECTORY: str = Paths.CONFIGURATION_DIRECTORY
    CONFIGURATION_FILE_NAME: str = Paths.CONFIGURATION_FILE_NAME
    CONFIGURATION_FILE_PATH = Paths.CONFIGURATION_FILE_PATH
    DEFAULT_CONNECTION_NAME = 'Default'

    def __init__(self):
        self.create_config_file()

    def get_config_data(self) -> object:
        self.connection_name = (input(f'Connection name (optional, default name {self.DEFAULT_CONNECTION_NAME}): ')
                                or self.DEFAULT_CONNECTION_NAME)
        self.local_path = input('Local path (optional): ')
        self.remote_path = (
            input(f'SSH remote path (optional, default will be created {Paths.DEFAULT_REMOTE_DIRECTORY_FOR_SYNCHRONIZATION}): ')
            or Paths.DEFAULT_REMOTE_DIRECTORY_FOR_SYNCHRONIZATION)
        self.host = input('Host IP or URL: ')
        self.port = int(input('Port (optional, default 22): ')) or 22
        self.user_name = input('User name: ')

        password = getpass(f'Password for {self.user_name}@{self.host}:{self.port}: ')
        state['password'] = password

        return {
            'connection_name': self.connection_name,
            'local_path': self.local_path,
            'remote_path': self.remote_path,
            'host': self.host,
            'user_name': self.user_name,
            'port': int(self.port),
        }

    def create_local_config_dir(self) -> None:
        if not isdir(self.CONFIGURATION_DIRECTORY):
            mkdir(self.CONFIGURATION_DIRECTORY)

    def load_settings(self, config_file_path: str) -> None:
        with open(config_file_path, 'r') as file:
            data = load(file)
            self.connection_name = data.get('connection_name')
            self.host = data.get('host')
            self.user_name = data.get('user_name')
            self.port = int(data.get('port'))
            self.remote_path = expanduser(data.get('remote_path'))
            self.local_path = expanduser(data.get('local_path'))

    def create_config_file(self) -> None:
        self.create_local_config_dir()

        if isfile(self.CONFIGURATION_FILE_PATH):
            try:
                self.load_settings(self.CONFIGURATION_FILE_PATH)
                return
            except JSONDecodeError:
                logger.error(f'Can not load JSON from config file located in '
                             f'{Paths.CONFIGURATION_FILE_PATH}. Retry credentials')
            except TypeError:
                logger.error('Wrong config file type. Retry credentials')
            except Exception as e:
                logger.error(f'Different error while decoding config file {e}')

        with open(self.CONFIGURATION_FILE_PATH, 'w') as file:
            config_data = self.get_config_data()
            dump(config_data, file, indent=4)
            file.close()

    def __getattr__(self, key):
        try:
            return self.config.get(key)
        except Exception as e:
            raise AttributeError(key)


config: ConfigService = ConfigService()

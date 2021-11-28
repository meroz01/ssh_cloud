from time import sleep

from paramiko.sftp import SFTPError

from src.constants.symbols import Symbols
from src.services.configuration_service import ConfigService
from src.services.files_listener_service import FilesListenerService
from src.services.internet_check_service import InternetCheckService
from src.services.logger_service import logger
from src.services.remote_service import RemoteService
from src.services.sftp_service import SFTPService


class SSHCloud:
    NO_INTERNET_CONNECTION_RETRY_TIME = 30

    def __init__(self):
        try:
            self.init()
        except IOError as e:
            logger.error(f'File error: {e}')
        except SFTPError as e:
            logger.error(f'SFTPError, {e}')
        except Exception as e:
            logger.error(f'Error occurred while initializing application: {e}')
        finally:
            pass

    @staticmethod
    def run_services():
        """
            Generate configuration
        """
        ConfigService()

        """
            Create connection to server
        """
        sftp: SFTPService = SFTPService()

        """
            Make some initial work on remote server
        """
        RemoteService(sftp).generate_remote_root_paths()

        """
            Create watcher to handle file change
        """

        files_listener_service: FilesListenerService = FilesListenerService(sftp)
        files_listener_service.run()

    def run_with_internet_connection(self, callback):
        is_online = InternetCheckService.is_online()

        if not is_online:
            logger.message(f'No internet connection, retry in {self.NO_INTERNET_CONNECTION_RETRY_TIME}s')
            sleep(self.NO_INTERNET_CONNECTION_RETRY_TIME)
            self.run_with_internet_connection(callback)

        callback()

    def init(self):
        logger.message(Symbols.START_BANNER)
        self.run_with_internet_connection(self.run_services)


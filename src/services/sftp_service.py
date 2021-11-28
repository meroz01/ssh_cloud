from datetime import datetime
from getpass import getpass
from json import dump
from os.path import join, dirname

from watchdog.events import FileSystemEvent
from paramiko import SSHClient, AutoAddPolicy
from paramiko.sftp_client import SFTPClient
from paramiko.ssh_exception import SSHException

from src.constants.symbols import Symbols
from src.constants.timestamp_paths import TimestampPaths
from src.helpers.paths_helper import PathsHelper
from src.helpers.state import state
from src.services.configuration_service import config
from src.services.logger_service import logger
from src.utils.progress_bar import ProgressBar


class SFTPService:
    SSH_CONNECTION_TIMEOUT = 10
    _paths_helper: PathsHelper = PathsHelper()
    __remote_path: str = config.remote_path
    __local_path: str = config.local_path

    def __init__(self):
        self.__sftp_client: SFTPClient = self.connect()

    def connect(self) -> SFTPClient | None:
        try:
            host_name_display: str = f'{config.user_name}@{config.host}:{config.port}'
            logger.message(f'{Symbols.CONNECTING} Connecting {host_name_display}')

            ssh_client: SSHClient = SSHClient()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy)

            password_from_state: str = state.get('password', '')

            if password_from_state:
                password: str = password_from_state
            else:
                password = getpass('Password: ')
                state['password'] = password

            credentials = {
                'hostname': config.host,
                'port': config.port,
                'username': config.user_name,
                'password': password,
                'timeout': self.SSH_CONNECTION_TIMEOUT
            }

            ssh_client.connect(**credentials)
            logger.message(f'{Symbols.CONNECTED} Connected!')

            return ssh_client.open_sftp()
        except SSHException as e:
            logger.error(e)
            return None

    def close_connection(self):
        self.__sftp_client.close()

    def get_file(self, remote_path: str, local_path: str) -> None:
        self.__sftp_client.get(remote_path, local_path, callback=ProgressBar.progress_info)

    def remove_file(self, event: FileSystemEvent):
        local_path, remote_path = self._paths_helper.get_paths_from_local_path(event.src_path)

        try:
            self.__sftp_client.remove(remote_path)
            logger.message(f'{Symbols.REMOVED} {remote_path} < {local_path}')
        except IOError:
            message = f'{Symbols.REMOVED_REMOTE} Already removed from remote: {local_path}'
            logger.error(message)
            logger.message(message)
        except Exception as e:
            message = f'Error while trying to remove from remote, {e}'
            logger.error(message)
            logger.message(message)

    def just_remove_file(self, remote_path):
        try:
            self.__sftp_client.remove(remote_path)
            logger.message(f'{Symbols.REMOVED_REMOTE} {remote_path}')
        except IOError:
            message = f'{Symbols.REMOVED_REMOTE} Already removed from remote: {remote_path}'
            logger.error(message)
            logger.message(message)
        except Exception as e:
            message = f'Error while trying to remove from remote, {e}'
            logger.error(message)
            logger.message(message)

    def put_file(self, given_local_path: str, is_directory: bool = False):
        local_path, remote_path = self._paths_helper.get_paths_from_local_path(given_local_path)

        self.put_directory(given_local_path, is_directory)

        try:
            self.__sftp_client.put(local_path, remote_path, ProgressBar.progress_info)
            self.run_after_transfer()
            logger.message(f'{Symbols.ADDED} {remote_path} < {local_path}')
        except OSError as e:
            logger.message(f'{Symbols.ERROR} Error for {remote_path} < {local_path}')
            logger.error(f'Error for {remote_path} < {local_path}, {e}')

    def make_directory(self, remote_directory: str):
        self.__sftp_client.mkdir(remote_directory)
        self.run_after_transfer()

    def get_directory(self):
        pass

    def rename(self, old_path, new_path):
        self.__sftp_client.rename(old_path, new_path)
        self.run_after_transfer()

    def remove_directory(self, event: FileSystemEvent):
        _, remote_path = self._paths_helper.get_paths_from_local_path(event.src_path)
        self._remove_directory(remote_path)

    def _remove_directory(self, remote_path: str):
        remote_directory_files = self.__sftp_client.listdir(remote_path)

        try:
            for file in remote_directory_files:
                item_remote_path = join(remote_path, file)

                if self.is_remote_directory(item_remote_path):
                    self._remove_directory(item_remote_path)
                else:
                    self.__sftp_client.remove(item_remote_path)

            self.__sftp_client.rmdir(remote_path)
            self.run_after_transfer()
        except IOError:
            logger.error(f'Can not remove directory {remote_path}')

    def _put_directories_recursively(self, local_directory_path, prev_remote_path: str = ''):
        if local_directory_path is None:
            return

        local_path, remote_path = self._paths_helper.get_paths_from_local_path(local_directory_path)

        if prev_remote_path:
            relative_path = remote_path.replace(prev_remote_path, '')
        else:
            relative_path = self._paths_helper.get_relative_path(local_directory_path, self.__local_path)

        paths = relative_path.strip('/').split('/')

        path_chunk = paths.pop(0)
        remote_path = (join(prev_remote_path, path_chunk)
                       if prev_remote_path
                       else join(self.__remote_path, path_chunk))

        if not self.does_directory_exist(remote_path):
            self.make_directory(remote_path)
            logger.message(f'{Symbols.CREATED} created directory: {remote_path}')

        if not len(paths):
            return

        self._put_directories_recursively(local_directory_path, remote_path)

    def put_directory(self, given_local_path: str, is_directory: bool) -> None:
        if given_local_path == config.local_path:
            return

        if is_directory:
            self._put_directories_recursively(given_local_path)

        strip_to_directory_path_details = dirname(given_local_path)
        self._put_directories_recursively(strip_to_directory_path_details)

    def does_directory_exist(self, curr_dir_check):
        try:
            self.__sftp_client.chdir(curr_dir_check)
            return True
        except IOError:
            return False
        except Exception as e:
            logger.error(e)
            return False

    def is_remote_directory(self, remote_path: str) -> bool:
        is_directory = False

        try:
            self.__sftp_client.listdir(remote_path)
            is_directory = True
        except IOError:
            pass

        return is_directory

    def get_directory_attributes(self, remote_path):
        return self.__sftp_client.listdir_attr(remote_path)

    def just_put_file(self, local_path: str, remote_path: str) -> None:
        self.__sftp_client.put(local_path, remote_path)

    def run_after_transfer(self):
        with open(TimestampPaths.TIMESTAMP_FILE_PATH, 'w') as file:
            now = datetime.now()
            timestamp = datetime.timestamp(now)

            data = {
                'last_sync': timestamp
            }

            dump(data, file, indent=4)
            file.close()

            self.just_put_file(TimestampPaths.TIMESTAMP_FILE_PATH, TimestampPaths.REMOTE_LOG_FILE_PATH)
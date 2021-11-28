import os
from os.path import join, dirname
from pathlib import Path
from typing import List

from src.constants.symbols import Symbols
from src.helpers.paths_helper import PathsHelper
from src.models.file_details import FileDetails
from src.services.sftp_service import SFTPService
from src.services.list_files_service import ListFilesService
from src.services.configuration_service import config
from src.services.logger_service import logger
from src.services.timestamp_service import TimestampService
from src.services.timing_service import TimingService


class ServerSynchronizationService:
    def __init__(self, sftp_service: SFTPService):
        self.__sftp_service: SFTPService = sftp_service
        self.__list_files_service = ListFilesService(sftp_service)
        self.__timestamp = TimestampService(sftp_service)
        self.__path_helper = PathsHelper()

    def synchronize(self):
        try:
            local_files = self.__list_files_service.get_local_files_list(base_path=config.local_path)
            remote_files = self.__list_files_service.get_remote_files_list(base_path=config.remote_path)

            logger.message(f'{Symbols.SYNCHRONIZING} Synchronizing...')

            self.copy_modified_files(local_files, remote_files)
            self.manage_missing_files(local_files, remote_files)
        except Exception as e:
            logger.error(f'Error while synchronizing files: {e}')

        self.__timestamp.save_timestamp()
        logger.message(f'{Symbols.SYNCHRONIZED} Synchronized at [{TimingService.time_stamp()}]')

    def manage_missing_files(self, local_files: List[FileDetails], remote_files: List[FileDetails]):
        is_local_latest = self.__timestamp.is_local_latest()

        local_relative_paths = [local.relative_path for local in local_files]
        remote_relative_paths = [remote.relative_path for remote in remote_files]

        missing_on_remote = list(filter(lambda x: x not in remote_relative_paths, local_relative_paths))
        missing_on_local = list(filter(lambda x: x not in local_relative_paths, remote_relative_paths))

        missing_on_remote_payload = list(filter(lambda x: x.relative_path in missing_on_remote, local_files))
        missing_on_local_payload = list(filter(lambda x: x.relative_path in missing_on_local, remote_files))

        for missing in missing_on_remote_payload:
            if is_local_latest:
                _, remote_path = self.__path_helper.get_paths_from_local_path(missing.src_path)
                self.__sftp_service.put_file(missing.src_path)
            else:
                os.remove(missing.src_path)

        for missing in missing_on_local_payload:
            new_local_path = join(config.local_path, missing.relative_path.strip('/'))

            if is_local_latest:
                self.__sftp_service.just_remove_file(missing.src_path)
            else:
                local_directory = dirname(new_local_path)
                Path(local_directory).mkdir(parents=True, exist_ok=True)
                self.__sftp_service.get_file(missing.src_path, new_local_path)

    def copy_modified_files(self, local_files: List[FileDetails], remote_files: List[FileDetails]):
        for local_file in local_files:
            for remote_file in remote_files:
                if (local_file.relative_path == remote_file.relative_path
                        and local_file.size != remote_file.size):
                    if local_file.modified >= remote_file.modified:
                        logger.message(f'{Symbols.ADDED} {local_file.src_path} > {remote_file.src_path}')
                        self.__sftp_service.put_file(local_file.src_path)
                        break
                    else:
                        logger.message(f'{Symbols.ADDED_LOCAL} {remote_file.src_path} > {local_file.src_path}')
                        self.__sftp_service.get_file(remote_file.src_path, local_file.src_path)
                        break

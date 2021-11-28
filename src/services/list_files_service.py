import math
import os
from os.path import join
from stat import S_ISDIR
from typing import List

from src.models.file_details import FileDetails
from src.services.sftp_service import SFTPService


class ListFilesService:
    def __init__(self, sftp_service: SFTPService):
        self.__sftp_service = sftp_service

    @staticmethod
    def get_local_files_list(local_path: str = '', base_path: str = '') -> List[FileDetails]:
        local_directories: List[FileDetails] = []

        if not local_path:
            local_path = base_path

        directories_list = os.listdir(local_path)

        for directory in directories_list:
            path = f'{local_path}/{directory}'
            is_dir = os.path.isdir(path)

            if is_dir:
                nested_directories = ListFilesService.get_local_files_list(f'{path}', base_path)
                local_directories = nested_directories + local_directories
            else:
                stat = os.stat(path)
                st_mtime = stat.st_mtime
                modified = math.ceil(st_mtime)
                size = stat.st_size

                compare_ob = FileDetails(path, base_path, size, modified)
                local_directories.append(compare_ob)

        return local_directories

    def get_remote_files_list(self, remote_path: str = '', base_path: str = ''):
        remote = []

        if not remote_path:
            remote_path = base_path

        files_list = self.__sftp_service.get_directory_attributes(remote_path)

        for file in files_list:
            is_dir = S_ISDIR(file.st_mode)
            filename = file.filename

            path = join(remote_path, filename)

            if is_dir:
                nested = self.get_remote_files_list(path, base_path)
                remote += nested
            else:
                modified = file.st_mtime
                size = file.st_size

                compare = FileDetails(path, base_path, size, modified)
                remote.append(compare)

        return remote

from src.helpers.paths_helper import PathsHelper
from src.services.sftp_service import SFTPService
from src.services.configuration_service import config


class RemoteService:
    _root_path: str = config.local_path
    _path_helper: PathsHelper = PathsHelper()

    def __init__(self, sftp_service: SFTPService):
        self.__sftp_service = sftp_service

    def generate_remote_root_paths(self) -> None:
        remote_base_path = config.remote_path

        if not self.__sftp_service.does_directory_exist(remote_base_path):
            self.__sftp_service.make_directory(remote_base_path)

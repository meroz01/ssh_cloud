from os.path import basename, join, isdir
from typing import Tuple

from src.services.configuration_service import config


class PathsHelper:
    _root_local_path: str = config.local_path
    _root_remote_path: str = config.remote_path

    def get_paths_from_local_path(self, given_local_path: str) -> Tuple[str, str]:
        relative_local_path = given_local_path.replace(self._root_local_path, '').strip('/')
        absolute_remote_path = join(self._root_remote_path, relative_local_path)
        return given_local_path, absolute_remote_path

    @staticmethod
    def get_relative_path(src_path: str, root_path: str) -> str:
        return src_path.replace(root_path, '')

    @staticmethod
    def get_remote_base_path(root_path: str) -> str:
        return join(config.remote_path, basename(root_path))

    def get_remote_full_path(self, src_path: str, root_path: str) -> str:
        relative_path = self.get_relative_path(src_path, root_path)
        remote_base_path = self.get_remote_base_path(root_path)
        return (join(remote_base_path, relative_path)
                if isdir(relative_path)
                else remote_base_path + relative_path)

    def is_root_path(self, src_path: str) -> bool:
        return any(root_path for root_path in self._root_local_path if root_path == src_path)

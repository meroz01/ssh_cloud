import re
from time import sleep
from typing import List, Dict

from watchdog.observers import Observer
from watchdog.events import (
    EVENT_TYPE_CREATED,
    EVENT_TYPE_DELETED,
    EVENT_TYPE_MOVED,
    FileSystemEvent,
    FileMovedEvent,
    PatternMatchingEventHandler)

from src.constants.symbols import Symbols
from src.helpers.paths_helper import PathsHelper
from src.services.configuration_service import config
from src.services.logger_service import logger
from src.services.server_synchronization_service import ServerSynchronizationService
from src.services.sftp_service import SFTPService


class FilesListenerService:
    WATCH_FILES_DURATION = 1
    TIME_TO_SYNCHRONIZE_SERVER_AND_LOCAL = 60
    _path: str = config.local_path
    _path_helper = PathsHelper()
    __counter = TIME_TO_SYNCHRONIZE_SERVER_AND_LOCAL
    __hidden_folders_pattern = '/\.|@[^/]'

    def __init__(self, sftp_service: SFTPService):
        self._sftp_service = sftp_service
        self._server_synchronization_service = ServerSynchronizationService(sftp_service)

    def run(self):
        self.synchronize_server_with_local_files()
        self.start_watchers()

    def synchronize_server_with_local_files(self):
        self._server_synchronization_service.synchronize()

    def start_watchers(self) -> None:
        event_handler = PatternMatchingEventHandler(case_sensitive=True)
        event_handler.on_any_event = self.event_callback

        observer = Observer()
        observer.schedule(event_handler, self._path, recursive=True)
        observer.start()

        logger.message(f'{Symbols.WATCHING} Watching: {self._path}')

        try:
            while True:
                sleep(self.WATCH_FILES_DURATION)

                if not self.__counter:
                    self._server_synchronization_service.synchronize()

                    self.__counter = self.TIME_TO_SYNCHRONIZE_SERVER_AND_LOCAL
                self.__counter -= self.WATCH_FILES_DURATION

        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    @property
    def watchdog_settings(self) -> Dict[str, str| bool | List[str]]:
        return {
            'ignore_directories': False,
            'ignore_patterns':  ['*.DS_Store'],
            'patterns': ['*.*']
        }

    def handle_created(self, event: FileSystemEvent):
        src_path = event.src_path
        is_directory = event.is_directory

        if event.is_directory:
            self._sftp_service.put_directory(src_path, is_directory)
        else:
            self._sftp_service.put_file(src_path, is_directory)

    def handle_deleted(self, event: FileSystemEvent):
        if event.is_directory:
            self._sftp_service.remove_directory(event)
        else:
            self._sftp_service.remove_file(event)

    def handle_moved(self, event: FileMovedEvent):
        _, old_remote_path = self._path_helper.get_paths_from_local_path(event.src_path)
        _, new_remote_path = self._path_helper.get_paths_from_local_path(event.dest_path)

        try:
            self._sftp_service.rename(old_remote_path, new_remote_path)
        except IOError as e:
            print(f'No such file to rename on remote {old_remote_path} > {new_remote_path}', e)

    def event_callback(self, event: FileSystemEvent | FileMovedEvent) -> None:
        event_type = event.event_type

        if re.match(self.__hidden_folders_pattern, event.src_path):
            return

        if event_type == EVENT_TYPE_CREATED:
            self.handle_created(event)

        if event_type == EVENT_TYPE_DELETED:
            self.handle_deleted(event)

        if event_type == EVENT_TYPE_MOVED:
            self.handle_moved(event)

from json import load, dump
from os import remove
from os.path import exists
from datetime import datetime
from typing import Tuple

from src.constants.timestamp_paths import TimestampPaths
from src.services.sftp_service import SFTPService


class TimestampService:
    def __init__(self, sftp_service: SFTPService = None):
        self.__sftp_service = sftp_service

    def is_local_latest(self) -> bool:
        local, remote = self.read_timestamps()
        return local >= remote

    def read_timestamps(self) -> Tuple[int, int]:
        local_time_stamp = 0
        remote_time_stamp = 0

        if exists(TimestampPaths.TIMESTAMP_FILE_PATH):
            with open(TimestampPaths.TIMESTAMP_FILE_PATH, 'r') as file:
                file_data = load(file)
                local_time_stamp = file_data.get('last_sync')

        self.__sftp_service.get_file(TimestampPaths.REMOTE_LOG_FILE_PATH, TimestampPaths.FETCHED_REMOTE_TIMESTAMP)

        if exists(TimestampPaths.FETCHED_REMOTE_TIMESTAMP):
            with open(TimestampPaths.FETCHED_REMOTE_TIMESTAMP, 'r') as file:
                file_data = load(file)
                if file_data:
                    remote_time_stamp = file_data.get('last_sync', '')
                    remove(TimestampPaths.FETCHED_REMOTE_TIMESTAMP)

        return local_time_stamp, remote_time_stamp

    def save_timestamp(self) -> None:
        with open(TimestampPaths.TIMESTAMP_FILE_PATH, 'w') as file:
            now = datetime.now()
            timestamp = datetime.timestamp(now)

            data = {
                'last_sync': timestamp
            }

            dump(data, file, indent=4)
            file.close()

            self.__sftp_service.just_put_file(TimestampPaths.TIMESTAMP_FILE_PATH, TimestampPaths.REMOTE_LOG_FILE_PATH)

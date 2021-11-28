from os.path import join

from src.constants.paths import Paths
from src.services.configuration_service import config


class TimestampPaths:
    LOG_FILE_NAME = '.sync_log'
    REMOTE_SYNC_FILE_NAME = '.remote_sync_log'
    REMOTE_LOG_FILE_PATH = join(config.remote_path, LOG_FILE_NAME)
    FETCHED_REMOTE_TIMESTAMP = join(Paths.CONFIGURATION_DIRECTORY, REMOTE_SYNC_FILE_NAME)
    TIMESTAMP_FILE_PATH = join(Paths.CONFIGURATION_DIRECTORY, FETCHED_REMOTE_TIMESTAMP)
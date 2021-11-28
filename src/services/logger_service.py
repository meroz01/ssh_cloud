import logging
from logging import Logger, getLogger, Formatter, StreamHandler, FileHandler

from src.utils.decorators.singleton import singleton


@singleton
class LoggerService:
    def __init__(self):
        self.logger: Logger = getLogger('SSHCloud')
        self.set_logger()

    def set_logger(self):
        terminal_handler = StreamHandler()
        terminal_handler.setLevel(logging.WARNING)
        terminal_format = Formatter('%(message)s')
        terminal_handler.setFormatter(terminal_format)
        self.logger.addHandler(terminal_handler)

        file_handler = FileHandler('report.log')
        file_handler.setLevel(logging.WARNING)
        file_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        error_handler = FileHandler('report.log')
        error_handler.setLevel(logging.ERROR)
        file_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.message(message)
        self.logger.error(message)

    def message(self, message):
        print(message)


logger: LoggerService = LoggerService()

import time
from datetime import datetime


class KeepRunning:
    @staticmethod
    def check_timing(callback):
        """
        :param callback: should be used as start and keep alive
        :return: any
        """
        callback()
        current_time = datetime.now()

        while True:
            time.sleep(1)
            diff = (datetime.now() - current_time).total_seconds()

            if diff > 10:
                callback()
                print('Run application after sleep')

            current_time = datetime.now()

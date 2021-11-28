from threading import Event
from src.services.logger_service import logger


class ProgressBar:
    DOWNLOADED_SYMBOL = '='
    NOT_DOWNLOADED_SYMBOL = '_'

    @staticmethod
    def progress_info(curr, total):
        if total < 100000:
            return

        total_line = 40
        percentage = round((curr / total) * 100)
        current = round((curr / total) * total_line)
        bar = f'[{current * ProgressBar.DOWNLOADED_SYMBOL}{(total_line - current) * ProgressBar.NOT_DOWNLOADED_SYMBOL}] {percentage} %'

        flush_with = '\n' if curr == total else '\r'
        print(bar, end=flush_with, flush=True)

    @staticmethod
    def time_counter(time, message, message2):
        event = Event()
        total = time

        while not event.wait(1):
            m = message if total % 2 == 0 else message2

            logger.message(f'{m} {total}s     ', end='\r')
            total = total - 1

            if not total:
                logger.message(f'{m} {total}s     ', end='\n')
                break

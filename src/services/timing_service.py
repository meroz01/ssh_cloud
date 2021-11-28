from datetime import datetime


class TimingService:
    @staticmethod
    def time_stamp():
        return datetime.now().strftime('%Y.%m.%d %H:%M:%S')

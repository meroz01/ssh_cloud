#!/usr/bin/env python3
from src.constants.symbols import Symbols
from src.ssh_cloud import SSHCloud
from src.utils.keep_running import KeepRunning


def run():
    SSHCloud()


if __name__ == '__main__':
    try:
        KeepRunning().check_timing(run)
    except KeyboardInterrupt:
        print(f'\n{Symbols.DISCONNECTED} Sync stopped!')
        exit(0)

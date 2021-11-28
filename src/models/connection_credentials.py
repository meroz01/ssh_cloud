from dataclasses import dataclass
from typing import List


@dataclass
class ConnectionCredentials(object):
    connection_name: str
    local_path: str
    remote_path: str
    host: str
    user_name: str
    port: int

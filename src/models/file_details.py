from src.helpers.paths_helper import PathsHelper


class FileDetails:
    def __init__(self, src_path: str, root_path: str, size: int, modified: int):
        self.root_path = root_path
        self.modified = modified
        self.size = size
        self.src_path = src_path
        self.relative_path = PathsHelper.get_relative_path(src_path, root_path)

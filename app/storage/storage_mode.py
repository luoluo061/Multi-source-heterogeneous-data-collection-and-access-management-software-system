from enum import Enum


class StorageMode(str, Enum):
    DB = "db"
    FILE = "file"

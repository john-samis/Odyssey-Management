"""
Contains the singleton logger for the application.

To be used in composition with all other classes.

"""
import logging


class AppLogger:
    """ House a singleton logger for the application"""

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            _instance = AppLogger()

    def __init__(self) -> None:
        pass
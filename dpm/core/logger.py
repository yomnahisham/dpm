"""
logger.py - structured logging system
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """structured logging system"""
    
    _instance: Optional['Logger'] = None
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        
        # create logger
        self.logger = logging.getLogger('dpm')
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # remove existing handlers
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # file handler
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(logging.DEBUG)  # always log everything to file
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # if file logging fails, continue without it
    
    @classmethod
    def instance(cls) -> 'Logger':
        """get singleton logger instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def initialize(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """initialize logger with config"""
        cls._instance = cls(log_level, log_file)
        return cls._instance
    
    def debug(self, message: str):
        """log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """log critical message"""
        self.logger.critical(message)


logger.py - structured logging system
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """structured logging system"""
    
    _instance: Optional['Logger'] = None
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        
        # create logger
        self.logger = logging.getLogger('dpm')
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # remove existing handlers
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # file handler
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(logging.DEBUG)  # always log everything to file
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # if file logging fails, continue without it
    
    @classmethod
    def instance(cls) -> 'Logger':
        """get singleton logger instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def initialize(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """initialize logger with config"""
        cls._instance = cls(log_level, log_file)
        return cls._instance
    
    def debug(self, message: str):
        """log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """log critical message"""
        self.logger.critical(message)


logger.py - structured logging system
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """structured logging system"""
    
    _instance: Optional['Logger'] = None
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        
        # create logger
        self.logger = logging.getLogger('dpm')
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # remove existing handlers
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # file handler
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(logging.DEBUG)  # always log everything to file
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # if file logging fails, continue without it
    
    @classmethod
    def instance(cls) -> 'Logger':
        """get singleton logger instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def initialize(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """initialize logger with config"""
        cls._instance = cls(log_level, log_file)
        return cls._instance
    
    def debug(self, message: str):
        """log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """log critical message"""
        self.logger.critical(message)


logger.py - structured logging system
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """structured logging system"""
    
    _instance: Optional['Logger'] = None
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        
        # create logger
        self.logger = logging.getLogger('dpm')
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # remove existing handlers
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # file handler
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(logging.DEBUG)  # always log everything to file
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # if file logging fails, continue without it
    
    @classmethod
    def instance(cls) -> 'Logger':
        """get singleton logger instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def initialize(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """initialize logger with config"""
        cls._instance = cls(log_level, log_file)
        return cls._instance
    
    def debug(self, message: str):
        """log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """log critical message"""
        self.logger.critical(message)




